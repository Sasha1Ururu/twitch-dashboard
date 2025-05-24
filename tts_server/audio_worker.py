import os
print("AUDIO_WORKER_FILE_VERSION_5_LOADED_FOR_TESTING") # Sanity print
import os
import time
import threading
import logging
import inspect # Ensure inspect is imported
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

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
        self.logger = logger if logger else default_logger # Logger needs to be set first
        # Diagnostic logging for db_session_factory (already added in Turn 110, re-applying to be sure)
        self.logger.info(f"AudioProcessingWorker INIT: db_session_factory type: {type(db_session_factory)}, id: {id(db_session_factory)}")
        if callable(db_session_factory):
            self.logger.info(f"AudioProcessingWorker INIT: db_session_factory name: {getattr(db_session_factory, '__name__', 'N/A')}, module: {getattr(db_session_factory, '__module__', 'N/A')}")
            actual_func_aw = db_session_factory 
            if hasattr(db_session_factory, '__wrapped__'): 
                 actual_func_aw = db_session_factory.__wrapped__
            elif hasattr(db_session_factory, 'func'): 
                 actual_func_aw = db_session_factory.func
            self.logger.info(f"AudioProcessingWorker INIT: actual_func_aw db_session_factory name: {getattr(actual_func_aw, '__name__', 'N/A')}, module: {getattr(actual_func_aw, '__module__', 'N/A')}")

        self.queue_manager = queue_manager
        self.tts_engine = tts_engine
        self.db_session_factory = db_session_factory
        
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
        # The content of this file was already updated in a previous turn (Turn 58)
        # to use the db_generator = self.db_session_factory(); db = next(db_generator); try...finally db.close()
        # pattern. This search block reflects the *already modified* state.
        # I am providing the same change again to ensure it's correctly applied if there was a reset or issue.
        db_generator = self.db_session_factory()
        db = next(db_generator)
        try:
            # Fetch messages with status DELETED that still have an audio_path
            # We don't need queue_type here, as we want to clean up all deleted audio.
            deleted_messages = db.query(TTSMessage).filter(
                    TTSMessage.status == MessageStatusEnum.DELETED,
                    TTSMessage.audio_path.isnot(None) # Only those with paths to clean
                ).all()

            if not deleted_messages: # Corrected indentation
                self.logger.debug("No DELETED messages with audio files to clean up.")
                # Ensure db is closed before returning if we got it from generator
                db.close() 
                return # Corrected indentation

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
        finally:
            # Ensure db is closed if it was successfully obtained from the generator
            if 'db' in locals() and hasattr(db, 'close'):
                db.close()

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
                    
                    # This block was also already modified in Turn 58. Re-applying for idempotency.
                    db_generator_process = self.db_session_factory()
                    db_process = next(db_generator_process)
                    try:
                        # Mark as PROCESSING
                        update_message_status(
                            db_process, 
                            message_id=message_to_process.id, 
                            new_status=MessageStatusEnum.PROCESSING,
                            processed_at=datetime.utcnow() # Set processed_at timestamp
                        )
                        db_process.commit() # Commit status change before synthesis
                        self.logger.debug(f"Message ID {message_to_process.id} status updated to PROCESSING.")
                        # Session is kept open for synthesis, then closed in finally if an error occurs early
                        # or explicitly before reopening for next update.

                        # Synthesize audio (outside the initial DB transaction for PROCESSING mark)
                        # Note: tts_engine.synthesize might be blocking.
                        # Output directory from global settings
                        audio_path, audio_size = self.tts_engine.synthesize(
                            message_id=message_to_process.id,
                            text_to_synthesize=message_to_process.text,
                            output_directory=settings.AUDIO_OUTPUT_DIRECTORY
                        )
                        # Close the session used for marking "PROCESSING" before opening a new one for update.
                        # This is important if synthesis is long and db_process might time out or lock.
                        db_process.close() 

                        db_generator_update = self.db_session_factory()
                        db_update = next(db_generator_update)
                        try:
                            if audio_path and audio_size > 0:
                                update_message_status(
                                    db_update,
                                    message_id=message_to_process.id,
                                    new_status=MessageStatusEnum.READY,
                                    audio_path=audio_path,
                                    audio_size_bytes=audio_size
                                )
                                db_update.commit()
                                self.logger.info(f"Message ID {message_to_process.id} processed successfully. Audio at: {audio_path}, Size: {audio_size} bytes.")
                            else:
                                self.logger.error(f"TTS synthesis failed for message ID {message_to_process.id}. No audio path or size returned.")
                                update_message_status(
                                    db_update,
                                    message_id=message_to_process.id,
                                    new_status=MessageStatusEnum.ERROR
                                )
                                db_update.commit()
                        finally:
                            db_update.close() # This finally block corresponds to the try for db_update
                            
                    except Exception as synth_exc: # This except block is for the outer try (db_process)
                        self.logger.error(f"Exception during synthesis or DB update for message ID {message_to_process.id}: {synth_exc}", exc_info=True)
                        # Ensure initial db_process is closed if it was still open from the 'try' part and an error occurred before its explicit close.
                        if 'db_process' in locals() and db_process.is_active: # Check if db_process was defined and is active
                             db_process.close()

                        db_generator_err = self.db_session_factory()
                        db_err = next(db_generator_err)
                        try: # Attempt to mark as ERROR
                            update_message_status(db_err, message_id=message_to_process.id, new_status=MessageStatusEnum.ERROR)
                            db_err.commit()
                        except Exception as db_update_err:
                            self.logger.error(f"Failed to update status to ERROR for message ID {message_to_process.id} after synthesis error: {db_update_err}", exc_info=True)
                        finally:
                            db_err.close() # This finally block corresponds to the try for db_err
                
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
