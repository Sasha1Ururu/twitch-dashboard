"""create_tts_messages_table

Revision ID: d16124bc5aa3
Revises: 
Create Date: 2025-05-24 02:46:59.160472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# Enum values for MessageStatusEnum, to avoid direct import from app code into migration
message_status_enum_values = (
    'PENDING', 'PROCESSING', 'READY', 'PLAYING', 'PLAYED', 'ERROR', 'DELETED'
)
message_status_enum = sa.Enum(*message_status_enum_values, name='messagestatusenum')


# revision identifiers, used by Alembic.
revision: str = 'd16124bc5aa3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('tts_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_type', sa.String(), nullable=False),
        sa.Column('sent_by', sa.String(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('bits_amount', sa.Integer(), nullable=True),
        sa.Column('status', message_status_enum, nullable=False, default='PENDING'),
        sa.Column('audio_path', sa.String(), nullable=True),
        sa.Column('audio_size_bytes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('played_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tts_messages_id'), 'tts_messages', ['id'], unique=False)
    op.create_index(op.f('ix_tts_messages_message_type'), 'tts_messages', ['message_type'], unique=False)
    op.create_index(op.f('ix_tts_messages_status'), 'tts_messages', ['status'], unique=False)
    op.create_index('ix_tts_messages_status_message_type', 'tts_messages', ['status', 'message_type'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_tts_messages_status_message_type', table_name='tts_messages')
    op.drop_index(op.f('ix_tts_messages_status'), table_name='tts_messages')
    op.drop_index(op.f('ix_tts_messages_message_type'), table_name='tts_messages')
    op.drop_index(op.f('ix_tts_messages_id'), table_name='tts_messages')
    op.drop_table('tts_messages')
    
    # Drop the enum type if it was created (specific to PostgreSQL, SQLite doesn't have separate enum types)
    # For SQLite, this is not strictly necessary as enums are usually handled as CHECK constraints or strings.
    # However, including it generally doesn't harm and is good practice for cross-DB compatibility if using native enums.
    # We need to ensure this is compatible with the DB dialect being used.
    # Since the default is SQLite, this might not be needed or might need conditional logic.
    # For now, we'll assume it's safe to call, or Alembic handles it.
    # A more robust way for PostgreSQL: message_status_enum.drop(op.get_bind(), checkfirst=True)
    # For this project, assuming SQLite where this will be a no-op or handled by Alembic.
    # Let's be more careful and check dialect for enum drop
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        message_status_enum.drop(bind, checkfirst=True)
    # For other dialects like SQLite, enums are often string constraints, so no explicit drop of type needed.
