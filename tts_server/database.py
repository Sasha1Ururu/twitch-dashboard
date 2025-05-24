from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum as SQLEnum, func, Index
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import List, Optional, Dict, Any
import enum
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class MessageStatusEnum(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    PLAYING = "PLAYING"
    PLAYED = "PLAYED"
    ERROR = "ERROR"
    DELETED = "DELETED"

class TTSMessage(Base):
    __tablename__ = "tts_messages"

    id = Column(Integer, primary_key=True, index=True)
    message_type = Column(String, nullable=False, index=True) # e.g., "mention", "bits"
    sent_by = Column(String, nullable=False)
    text = Column(String, nullable=False)
    bits_amount = Column(Integer, nullable=True)
    status = Column(SQLEnum(MessageStatusEnum), default=MessageStatusEnum.PENDING, nullable=False, index=True)
    audio_path = Column(String, nullable=True)
    audio_size_bytes = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    played_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_tts_messages_status_message_type', 'status', 'message_type'),
    )


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Placeholder CRUD and query functions
def add_message(db_session: Session, message_data: Dict[str, Any]) -> TTSMessage:
    """Adds a new message to the database."""
    new_message = TTSMessage(**message_data)
    db_session.add(new_message)
    db_session.commit()
    db_session.refresh(new_message)
    return new_message

def get_message_by_id(db_session: Session, message_id: int) -> Optional[TTSMessage]:
    """Retrieves a message by its ID."""
    return db_session.query(TTSMessage).filter(TTSMessage.id == message_id).first()

def update_message_status(db_session: Session, message_id: int, new_status: MessageStatusEnum, **kwargs: Any) -> Optional[TTSMessage]:
    """Updates the status and other fields of a message."""
    message = db_session.query(TTSMessage).filter(TTSMessage.id == message_id).first()
    if message:
        message.status = new_status
        for key, value in kwargs.items():
            if hasattr(message, key):
                setattr(message, key, value)
            else:
                # Consider logging a warning for unexpected kwargs
                print(f"Warning: Field {key} not found in TTSMessage model.")
        db_session.commit()
        db_session.refresh(message)
    return message

def get_messages_by_status(db_session: Session, status: MessageStatusEnum, queue_type: Optional[str] = None, limit: int = 10) -> List[TTSMessage]:
    """Retrieves messages by status, optionally filtered by message_type."""
    query = db_session.query(TTSMessage).filter(TTSMessage.status == status)
    if queue_type:
        query = query.filter(TTSMessage.message_type == queue_type)
    
    query = query.order_by(TTSMessage.created_at)
    if limit != -1: # Apply limit only if it's not -1 (meaning "all")
        query = query.limit(limit)
    return query.all()

def get_oldest_message_for_processing(db_session: Session, queue_type: str) -> Optional[TTSMessage]:
    """Gets the oldest PENDING message of a specific queue_type."""
    return db_session.query(TTSMessage)\
        .filter(TTSMessage.status == MessageStatusEnum.PENDING, TTSMessage.message_type == queue_type)\
        .order_by(TTSMessage.created_at)\
        .first()

def get_oldest_ready_message(db_session: Session, queue_type: str) -> Optional[TTSMessage]:
    """Gets the oldest READY message of a specific queue_type."""
    return db_session.query(TTSMessage)\
        .filter(TTSMessage.status == MessageStatusEnum.READY, TTSMessage.message_type == queue_type)\
        .order_by(TTSMessage.created_at)\
        .first()

def get_total_audio_size(db_session: Session, queue_type: str) -> int:
    """Calculates the total audio_size_bytes for READY messages in the specified queue_type."""
    total_size = db_session.query(func.sum(TTSMessage.audio_size_bytes))\
        .filter(TTSMessage.message_type == queue_type,
                TTSMessage.status == MessageStatusEnum.READY,
                TTSMessage.audio_size_bytes.isnot(None))\
        .scalar()
    return total_size or 0

def get_messages_to_delete_for_overflow(db_session: Session, queue_type: str, size_to_free: int) -> List[TTSMessage]:
    """
    Identifies the oldest READY messages with audio_size_bytes to be marked as DELETED 
    to free up at least `size_to_free` bytes for the given `queue_type`.
    Returns a list of TTSMessage objects to be deleted.
    """
    messages_to_delete = []
    if size_to_free <= 0:
        return messages_to_delete

    # Fetch oldest READY messages that have an audio_size_bytes
    candidates = db_session.query(TTSMessage)\
        .filter(TTSMessage.message_type == queue_type,
                TTSMessage.status == MessageStatusEnum.READY,
                TTSMessage.audio_size_bytes.isnot(None))\
        .order_by(TTSMessage.created_at)\
        .all()
    
    freed_size_accumulator = 0
    for msg in candidates:
        if freed_size_accumulator >= size_to_free:
            break
        if msg.audio_size_bytes and msg.audio_size_bytes > 0: # Ensure it contributes to freeing space
            messages_to_delete.append(msg)
            freed_size_accumulator += msg.audio_size_bytes
            
    # If after checking all READY messages with sizes, we haven't freed enough,
    # this function currently does not fall back to PENDING messages,
    # as their future size is unknown. This could be a point of future refinement.
    # For now, it only returns messages that it's sure will contribute to reducing byte size.
    
    # If we still haven't met `size_to_free` it means there are not enough READY messages
    # with recorded sizes to delete. The current implementation will return what it found.
    # The caller (QueueManager) should be aware that the returned list might not free enough space
    # if there are few sizeable READY messages.

    return messages_to_delete


def mark_messages_as_deleted(db_session: Session, message_ids: List[int]) -> int:
    """Marks messages as DELETED by their IDs and sets deleted_at."""
    if not message_ids:
        return 0
    
    updated_count = db_session.query(TTSMessage)\
        .filter(TTSMessage.id.in_(message_ids), TTSMessage.status != MessageStatusEnum.DELETED)\
        .update({
            TTSMessage.status: MessageStatusEnum.DELETED,
            TTSMessage.deleted_at: func.now()
        }, synchronize_session=False) # 'fetch' can also be used
    
    db_session.commit()
    return updated_count
