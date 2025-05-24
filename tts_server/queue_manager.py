import os
import logging
from sqlalchemy.orm import Session
from typing import Optional, Callable, Dict, Any, List

from .database import (
    TTSMessage,
    MessageStatusEnum,
    add_message,
    get_oldest_message_for_processing,
    get_oldest_ready_message,
    get_total_audio_size,
    get_messages_to_delete_for_overflow,
    mark_messages_as_deleted,
    get_messages_by_status,
    # get_db # Not imported directly, but session_factory will use it
)
from .config import settings # To access MENTIONS_QUEUE_MAX_AUDIO_BYTES if defined there, or use a local const

# Default logger if none is provided to the class
default_logger = logging.getLogger(__name__)

class QueueManager:
    def __init__(self, db_session_factory: Callable[[], Session], logger: Optional[logging.Logger] = None):
        """
        Initializes the QueueManager.
        Args:
            db_session_factory: A callable that provides a DB session (e.g., get_db).
            logger: A Python logger instance. Uses a default logger if None.
        """
        self.db_session_factory = db_session_factory
        self.logger = logger if logger else default_logger
        self.active_queue_type: str = "mentions"  # Default active queue
        
        # Max audio bytes for the "mentions" queue (e.g., 200MB)
        # This could also come from settings if made configurable there.
        self.MENTIONS_QUEUE_MAX_AUDIO_BYTES = 200 * 1024 * 1024 
        
        self.logger.info(f"QueueManager initialized. Active queue: '{self.active_queue_type}'. Mentions max audio: {self.MENTIONS_QUEUE_MAX_AUDIO_BYTES / (1024*1024)}MB.")

    def add_message_to_queue(self, message_data: Dict[str, Any]) -> Optional[TTSMessage]:
        """
        Adds a message to the appropriate queue in the database and handles overflow for mentions.
        Args:
            message_data: Dictionary with message details compatible with database.add_message.
                          Must include 'message_type' ("mentions" or "bits").
        Returns:
            The created TTSMessage object or None if creation failed.
        """
        queue_type = message_data.get("message_type")
        if not queue_type or queue_type not in ["mentions", "bits"]:
            self.logger.error(f"Invalid or missing 'message_type' in message_data: {queue_type}. Message not added.")
            return None

        self.logger.info(f"Attempting to add message to '{queue_type}' queue: {message_data.get('text', '')[:50]}...")

        try:
            with self.db_session_factory() as db:
                # Add the message to the database
                new_message = add_message(db, message_data)
                self.logger.info(f"Message ID {new_message.id} (type: {queue_type}) added to DB with status PENDING.")

                # Overflow management for "mentions" queue
                if queue_type == "mentions":
                    current_total_size = get_total_audio_size(db, queue_type="mentions")
                    self.logger.debug(f"Current total audio size for 'mentions' queue: {current_total_size / (1024*1024):.2f}MB.")
                    
                    if current_total_size > self.MENTIONS_QUEUE_MAX_AUDIO_BYTES:
                        size_to_free = current_total_size - self.MENTIONS_QUEUE_MAX_AUDIO_BYTES
                        self.logger.warning(
                            f"'mentions' queue size ({current_total_size / (1024*1024):.2f}MB) "
                            f"exceeds limit ({self.MENTIONS_QUEUE_MAX_AUDIO_BYTES / (1024*1024):.2f}MB). "
                            f"Need to free {size_to_free / (1024*1024):.2f}MB."
                        )
                        
                        # Get oldest READY messages to delete to free up space
                        messages_to_remove = get_messages_to_delete_for_overflow(db, queue_type="mentions", size_to_free=size_to_free)
                        
                        if messages_to_remove:
                            ids_to_remove = [msg.id for msg in messages_to_remove]
                            self.logger.info(f"Overflow: Marking {len(ids_to_remove)} messages for deletion: {ids_to_remove}")
                            
                            # Mark messages as DELETED in DB
                            # Note: `mark_messages_as_deleted` already takes `message_ids`.
                            # The `new_status` parameter was not in its original definition,
                            # it implicitly sets status to DELETED.
                            count_deleted = mark_messages_as_deleted(db, message_ids=ids_to_remove)
                            self.logger.info(f"{count_deleted} messages marked as DELETED due to overflow.")
                        else:
                            self.logger.warning("Overflow condition, but no suitable messages found to delete to free space.")
                return new_message
        except Exception as e:
            self.logger.error(f"Error adding message to queue: {e}", exc_info=True)
            return None

    def get_next_message_to_process(self) -> Optional[TTSMessage]:
        """
        Retrieves the oldest PENDING message from the currently active queue.
        Returns:
            TTSMessage object or None if no message is pending.
        """
        self.logger.debug(f"Checking for next message to process in '{self.active_queue_type}' queue.")
        try:
            with self.db_session_factory() as db:
                message = get_oldest_message_for_processing(db, queue_type=self.active_queue_type)
                if message:
                    self.logger.info(f"Found PENDING message ID {message.id} in '{self.active_queue_type}' queue to process.")
                else:
                    self.logger.debug(f"No PENDING messages in '{self.active_queue_type}' queue.")
                return message
        except Exception as e:
            self.logger.error(f"Error getting next message to process: {e}", exc_info=True)
            return None

    def get_next_message_to_play(self) -> Optional[TTSMessage]:
        """
        Retrieves the oldest READY message from the currently active queue.
        Returns:
            TTSMessage object or None if no message is ready.
        """
        self.logger.debug(f"Checking for next message to play in '{self.active_queue_type}' queue.")
        try:
            with self.db_session_factory() as db:
                message = get_oldest_ready_message(db, queue_type=self.active_queue_type)
                if message:
                    self.logger.info(f"Found READY message ID {message.id} in '{self.active_queue_type}' queue to play.")
                else:
                    self.logger.debug(f"No READY messages in '{self.active_queue_type}' queue.")
                return message
        except Exception as e:
            self.logger.error(f"Error getting next message to play: {e}", exc_info=True)
            return None

    def clear_active_queue(self) -> int:
        """
        Marks all PENDING and READY messages in the active queue as DELETED.
        Audio file deletion is handled by the AudioWorker upon seeing DELETED status.
        Returns:
            The number of messages marked as DELETED.
        """
        self.logger.info(f"Attempting to clear PENDING and READY messages from '{self.active_queue_type}' queue.")
        cleared_count = 0
        try:
            with self.db_session_factory() as db:
                # Fetch all PENDING messages for the active queue type
                pending_messages = get_messages_by_status(db, status=MessageStatusEnum.PENDING, queue_type=self.active_queue_type, limit=-1) # -1 for all
                # Fetch all READY messages for the active queue type
                ready_messages = get_messages_by_status(db, status=MessageStatusEnum.READY, queue_type=self.active_queue_type, limit=-1)
                
                ids_to_clear = [msg.id for msg in pending_messages + ready_messages]
                
                if ids_to_clear:
                    self.logger.info(f"Found {len(ids_to_clear)} messages to mark as DELETED in '{self.active_queue_type}' queue.")
                    # The `mark_messages_as_deleted` function handles setting status to DELETED.
                    cleared_count = mark_messages_as_deleted(db, message_ids=ids_to_clear)
                    self.logger.info(f"Successfully marked {cleared_count} messages as DELETED from '{self.active_queue_type}' queue.")
                else:
                    self.logger.info(f"No PENDING or READY messages found in '{self.active_queue_type}' queue to clear.")
            return cleared_count
        except Exception as e:
            self.logger.error(f"Error clearing active queue '{self.active_queue_type}': {e}", exc_info=True)
            return 0


    def get_active_queue_stats(self) -> Dict[str, Any]:
        """
        Provides statistics for the currently active queue.
        Returns:
            A dictionary with queue statistics.
        """
        self.logger.debug(f"Getting stats for active queue: '{self.active_queue_type}'.")
        stats: Dict[str, Any] = {
            "active_queue_type": self.active_queue_type,
            "pending_count": 0,
            "ready_count": 0,
            "mentions_total_audio_size_bytes": 0, # Only relevant if active_queue_type is "mentions"
                                                 # but included for consistency; calculation specific to "mentions"
            "error_count": 0, # Example of an additional stat one might want
            "processing_count": 0
        }
        try:
            with self.db_session_factory() as db:
                pending_messages = get_messages_by_status(db, status=MessageStatusEnum.PENDING, queue_type=self.active_queue_type, limit=-1)
                stats["pending_count"] = len(pending_messages)
                
                ready_messages = get_messages_by_status(db, status=MessageStatusEnum.READY, queue_type=self.active_queue_type, limit=-1)
                stats["ready_count"] = len(ready_messages)

                error_messages = get_messages_by_status(db, status=MessageStatusEnum.ERROR, queue_type=self.active_queue_type, limit=-1)
                stats["error_count"] = len(error_messages)

                processing_messages = get_messages_by_status(db, status=MessageStatusEnum.PROCESSING, queue_type=self.active_queue_type, limit=-1)
                stats["processing_count"] = len(processing_messages)

                # Calculate total audio size for the "mentions" queue, regardless of active queue
                # The key name suggests it's specific to mentions queue.
                stats["mentions_total_audio_size_bytes"] = get_total_audio_size(db, queue_type="mentions")
                
            self.logger.debug(f"Stats for '{self.active_queue_type}': {stats}")
        except Exception as e:
            self.logger.error(f"Error getting active queue stats: {e}", exc_info=True)
            # Return empty/default stats on error
        return stats

    def switch_active_queue(self, new_queue_type: str) -> bool:
        """
        Switches the active queue type.
        Args:
            new_queue_type: The type of queue to switch to ("mentions" or "bits").
        Returns:
            True if switched, False otherwise (e.g., invalid type or already active).
        """
        self.logger.info(f"Request to switch active queue from '{self.active_queue_type}' to '{new_queue_type}'.")
        if new_queue_type not in ["mentions", "bits"]:
            self.logger.warning(f"Invalid queue type for switch: '{new_queue_type}'. Must be 'mentions' or 'bits'.")
            return False
        
        if self.active_queue_type == new_queue_type:
            self.logger.info(f"Queue type '{new_queue_type}' is already active. No switch needed.")
            return False # Or True, depending on desired semantics for "no change needed"

        # Persistently save current queue state (e.g. in DB or a file if needed)
        # For this design, the state is primarily in the database (message statuses).
        # If there were in-memory buffers or specific states tied to the active queue
        # that are not in the DB, they would be finalized here.
        # Example: If worker had an in-memory item for `active_queue_type`, tell worker to pause/finalize.
        # Currently, AudioWorker pulls from DB based on `active_queue_type` passed to its methods
        # or if it holds a reference to QueueManager, it would see the change.
        # For now, simply changing the type is sufficient as workers will pick up from the new queue.
        
        self.active_queue_type = new_queue_type
        self.logger.info(f"Active queue switched to '{self.active_queue_type}'.")
        
        # TODO: Consider if any notification or state reset is needed for workers
        # e.g., if a worker is processing a message from the old queue type.
        # The current design implies workers fetch based on the active queue at time of fetch.
        
        return True

# Note: No global instance of QueueManager should be created here.
# It will be instantiated in main.py or a similar central place.
