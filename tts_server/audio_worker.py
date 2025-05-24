import os
import time
import threading
import logging
from sqlalchemy.orm import Session # For type hinting if needed, direct use minimized
from datetime import datetime # For setting processed_at

from .database import (
    TTSMessage,         # For type hinting
    MessageStatusEnum,
    # get_db,           # db_session_factory will be passed, typically using get_db
    update_message_status,
    get_messages_by_status
)
from .queue_manager import QueueManager
from .tts_engine import TTSEngine
from .config import settings

# Default logger if none is provided to the class
default_logger = logging.getLogger(__name__)

class AudioProcessingWorker:
    def __init__(self, 
                 queue_manager: QueueManager, 
                 tts_engine: TTSEngine, 
                 db_session_factory: callable, # e.g., tts_server.database.get_db
                 logger: Optional[logging.Logger] = None):
        """
        Initializes the AudioProcessingWorker.
        Args:
            queue_manager: Instance of QueueManager.
            tts_engine: Instance of TTSEngine.
            db_session_factory: A callable that provides a DB session.
            logger: A Python logger instance. Uses a default logger if None.
        """
        self.queue_manager = queue_manager
        self.tts_engine = tts_engine
        self.db_session_factory = db_session_factory
        self.logger = logger if logger else default_logger
        
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.logger.info("AudioProcessingWorker initialized.")

    def start(self):
        """Starts the worker thread."""
        if self.thread.is_alive():
            self.logger.warning("Attempted to start worker thread, but it's already running.")
            return
        self.logger.info("Starting AudioProcessingWorker thread...")
        self._stop_event.clear() # Ensure stop event is clear before starting
        self.thread.start()
        self.logger.info("AudioProcessingWorker thread started.")

    def stop(self):
        """Signals the worker thread to stop and waits for it to join."""
        self.logger.info("Stopping AudioProcessingWorker thread...")
        self._stop_event.set()
        
        # Wait for the thread to finish. Add a timeout for safety.
        # Daemon threads don't strictly need joining for program exit,
        # but it's good practice for graceful shutdown if time allows.
        try:
            self.thread.join(timeout=settings.WORKER_POLL_INTERVAL * 5) # Wait up to 5 poll intervals
            if self.thread.is_alive():
                self.logger.warning("AudioProcessingWorker thread did not stop in time.")
            else:
                self.logger.info("AudioProcessingWorker thread stopped successfully.")
        except Exception as e:
            self.logger.error(f"Error joining worker thread: {e}", exc_info=True)


    def _handle_deleted_messages(self):
        """Handles deletion of audio files for messages marked as DELETED."""
        self.logger.debug("Checking for messages marked DELETED to clean up audio files...")
        try:
            with self.db_session_factory() as db:
                # Fetch messages with status DELETED that still have an audio_path
                # We don't need queue_type here, as we want to clean up all deleted audio.
                deleted_messages = db.query(TTSMessage).filter(
                    TTSMessage.status == MessageStatusEnum.DELETED,
                    TTSMessage.audio_path.isnot(None) # Only those with paths to clean
                ).all()

                if not deleted_messages:
                    self.logger.debug("No DELETED messages with audio files to clean up.")
                    return

                self.logger.info(f"Found {len(deleted_messages)} DELETED messages with audio files to clean.")
                for msg in deleted_messages:
                    if msg.audio_path and os.path.exists(msg.audio_path):
                        try:
                            os.remove(msg.audio_path)
                            self.logger.info(f"Successfully deleted audio file: {msg.audio_path} for message ID {msg.id}.")
                            # Update message to nullify audio_path to prevent re-processing
                            update_message_status(db, message_id=msg.id, new_status=MessageStatusEnum.DELETED, audio_path=None)
                            self.logger.debug(f"Nullified audio_path for message ID {msg.id}.")
                        except OSError as e:
                            self.logger.error(f"Error deleting audio file {msg.audio_path} for message ID {msg.id}: {e}", exc_info=True)
                            # Optionally, update status to ERROR or keep as DELETED but log the issue.
                            # For now, it will remain DELETED with path, and retry deletion next cycle.
                            # Or, to prevent retry loops on permission errors, nullify path anyway or use a sub-status.
                            # Let's nullify to avoid repeated attempts on files that might be problematic (e.g. locked)
                            update_message_status(db, message_id=msg.id, new_status=MessageStatusEnum.DELETED, audio_path=None)
                            self.logger.warning(f"Nullified audio_path for message ID {msg.id} after deletion error to prevent retries.")
                    elif msg.audio_path: # Path exists in DB but not on disk
                        self.logger.warning(f"Audio file {msg.audio_path} for DELETED message ID {msg.id} not found on disk. Nullifying path.")
                        update_message_status(db, message_id=msg.id, new_status=MessageStatusEnum.DELETED, audio_path=None)
        except Exception as e:
            self.logger.error(f"Error in _handle_deleted_messages: {e}", exc_info=True)


    def _process_loop(self):
        """Main loop for the worker thread."""
        self.logger.info("AudioProcessingWorker process loop started.")
        
        while not self._stop_event.is_set():
            try:
                # 1. Process Deletions
                self._handle_deleted_messages()
                if self._stop_event.is_set(): break # Check stop event after potentially long operation

                # 2. Process New Messages
                message_to_process = self.queue_manager.get_next_message_to_process()

                if message_to_process:
                    self.logger.info(f"Processing message ID {message_to_process.id} (Type: {message_to_process.message_type}, Text: '{message_to_process.text[:30]}...')")
                    
                    try:
                        with self.db_session_factory() as db:
                            # Mark as PROCESSING
                            update_message_status(
                                db, 
                                message_id=message_to_process.id, 
                                new_status=MessageStatusEnum.PROCESSING,
                                processed_at=datetime.utcnow() # Set processed_at timestamp
                            )
                            db.commit() # Commit status change before synthesis
                            self.logger.debug(f"Message ID {message_to_process.id} status updated to PROCESSING.")

                        # Synthesize audio
                        # Note: tts_engine.synthesize might be blocking. Consider if it needs to be interruptible.
                        # Output directory from global settings
                        audio_path, audio_size = self.tts_engine.synthesize(
                            message_id=message_to_process.id,
                            text_to_synthesize=message_to_process.text,
                            output_directory=settings.AUDIO_OUTPUT_DIRECTORY
                            # TTS_ENGINE_SPEED is used by TTSEngine's constructor, not per synthesis call in current TTSEngine design
                        )
                        
                        with self.db_session_factory() as db:
                            if audio_path and audio_size > 0:
                                update_message_status(
                                    db,
                                    message_id=message_to_process.id,
                                    new_status=MessageStatusEnum.READY,
                                    audio_path=audio_path,
                                    audio_size_bytes=audio_size
                                )
                                db.commit()
                                self.logger.info(f"Message ID {message_to_process.id} processed successfully. Audio at: {audio_path}, Size: {audio_size} bytes.")
                            else:
                                self.logger.error(f"TTS synthesis failed for message ID {message_to_process.id}. No audio path or size returned.")
                                update_message_status(
                                    db,
                                    message_id=message_to_process.id,
                                    new_status=MessageStatusEnum.ERROR
                                    # Potentially add an error message field to TTSMessage model
                                )
                                db.commit()
                    except Exception as synth_exc:
                        self.logger.error(f"Exception during synthesis or DB update for message ID {message_to_process.id}: {synth_exc}", exc_info=True)
                        try: # Attempt to mark as ERROR
                            with self.db_session_factory() as db_err:
                                update_message_status(db_err, message_id=message_to_process.id, new_status=MessageStatusEnum.ERROR)
                                db_err.commit()
                        except Exception as db_update_err:
                            self.logger.error(f"Failed to update status to ERROR for message ID {message_to_process.id} after synthesis error: {db_update_err}", exc_info=True)
                
                else: # No message to process
                    self.logger.debug(f"No message to process from queue '{self.queue_manager.active_queue_type}'. Sleeping for {settings.WORKER_POLL_INTERVAL}s.")
                    # Use the event's wait method for interruptible sleep
                    self._stop_event.wait(timeout=settings.WORKER_POLL_INTERVAL)

            except Exception as e:
                self.logger.error(f"Unexpected error in AudioProcessingWorker loop: {e}", exc_info=True)
                # Sleep for a bit to prevent rapid-fire error loops if the error is persistent
                self._stop_event.wait(timeout=settings.WORKER_POLL_INTERVAL * 5) # Longer sleep on unexpected error

        self.logger.info("AudioProcessingWorker process loop stopped.")

# No global instances. Worker managed in main.py.
