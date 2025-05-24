import os
import threading
import time
import logging
from pathlib import Path # For path manipulation if needed for static files

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import create_db_and_tables, get_db # Using existing create_db_and_tables as init_db
from .tts_engine import TTSEngine
from .queue_manager import QueueManager
from .audio_worker import AudioProcessingWorker
from .api import router as api_router
from . import api as api_module # To access/override elements within api.py

# 1. Setup Logging
# Format includes logger name for clarity
logging.basicConfig(
    level=settings.LOG_LEVEL.upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 2. FastAPI App Instance
app = FastAPI(title="TTS Server")

# 3. Global Application State
# To hold instances of worker, queue manager, tts engine, etc.
app_state: dict = {}

# 4. Autoplay Thread Global Stop Event
autoplay_thread_stop_event = threading.Event()

# 5. Dependency Injection for QueueManager
def get_queue_manager_dependency() -> QueueManager:
    qm = app_state.get('queue_manager')
    if qm is None:
        # This case should ideally not be hit if startup event completes successfully
        logger.critical("QueueManager not found in app_state for dependency injection!")
        # Depending on strictness, could raise an error or try to initialize.
        # For now, let's assume it's always populated by startup.
        raise RuntimeError("QueueManager not initialized")
    return qm

# 6. Autoplay Loop Function
def autoplay_loop(db_session_factory: callable, queue_manager_instance: QueueManager, logger_instance: logging.Logger):
    logger_instance.info("Autoplay loop started.")
    while not autoplay_thread_stop_event.is_set():
        if api_module.autoplay_enabled: # Check the global autoplay_enabled flag from api.py
            try:
                # QueueManager methods are designed to create their own DB sessions via the factory
                message = queue_manager_instance.get_next_message_to_play()
                
                if message:
                    logger_instance.info(f"[Autoplay] Triggering play for message ID: {message.id} (Text: '{message.text[:30]}...')")
                    
                    # Mark as PLAYING using a fresh session
                    with db_session_factory() as db:
                        from tts_server.database import update_message_status, MessageStatusEnum # Local import for clarity
                        from datetime import datetime # Local import for clarity
                        update_message_status(
                            db, 
                            message_id=message.id, 
                            new_status=MessageStatusEnum.PLAYING, 
                            played_at=datetime.utcnow()
                        )
                        # Note: The actual audio playback is handled by the client.
                        # This loop just signals that a message *should* be played by updating its status.
                        # The client would then presumably fetch this message via an API call.
                        # If the client calls /play_next itself, this autoplay logic might conflict or be redundant
                        # depending on how client fetches. This assumes client watches for PLAYING status
                        # or there's another mechanism.
                        # For now, let's assume the client polls /play_next or similar.
                        # The cooldown here means we don't rapidly mark messages as PLAYING.
                    
                    logger_instance.info(f"[Autoplay] Message ID {message.id} marked as PLAYING. Waiting for cooldown: {settings.AUTOPLAY_COOLDOWN}s.")
                    # Wait for the cooldown period or until stop event is set
                    autoplay_thread_stop_event.wait(settings.AUTOPLAY_COOLDOWN)
                else:
                    logger_instance.debug("[Autoplay] No message ready to play. Waiting for poll interval.")
                    autoplay_thread_stop_event.wait(settings.WORKER_POLL_INTERVAL)
            except Exception as e:
                logger_instance.error(f"[Autoplay] Error in autoplay loop: {e}", exc_info=True)
                # Wait for cooldown on error to prevent rapid failing loops
                autoplay_thread_stop_event.wait(settings.AUTOPLAY_COOLDOWN)
        else:
            logger_instance.debug("[Autoplay] Autoplay is disabled. Waiting for poll interval.")
            autoplay_thread_stop_event.wait(settings.WORKER_POLL_INTERVAL)
    
    logger_instance.info("Autoplay loop stopped.")

# 7. FastAPI Startup Event
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup sequence initiated...")

    # Initialize Database (create tables if they don't exist)
    logger.info("Initializing database...")
    create_db_and_tables() # Using existing function as init_db
    logger.info("Database initialization complete.")

    # Initialize TTS Engine
    logger.info("Initializing TTSEngine...")
    tts_engine_logger = logging.getLogger("tts_engine")
    try:
        tts_engine_instance = TTSEngine(
            lang_code=settings.KOKORO_LANG_CODE, # Ensure this is the correct setting for KPipeline
            voice_config_str=settings.VOICE_CONFIG_STR,
            voice_mappings=settings.parsed_voice_mappings, # Already parsed by Pydantic
            tts_speed=settings.TTS_ENGINE_SPEED,
            logger=tts_engine_logger
        )
        app_state['tts_engine'] = tts_engine_instance
        logger.info("TTSEngine initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize TTSEngine: {e}", exc_info=True)
        # Decide if app should fail to start or run in a degraded mode
        # For now, let it continue, but TTS functionality will be broken.
        app_state['tts_engine'] = None # Mark as None to indicate failure

    # Initialize Queue Manager
    logger.info("Initializing QueueManager...")
    queue_manager_logger = logging.getLogger("queue_manager")
    queue_manager_instance = QueueManager(
        db_session_factory=get_db, # Pass the session factory
        logger=queue_manager_logger
    )
    app_state['queue_manager'] = queue_manager_instance
    logger.info("QueueManager initialized successfully.")

    # Override placeholder in api.py with the actual dependency function
    logger.info("Setting up QueueManager dependency for API routes...")
    api_module.get_queue_manager = get_queue_manager_dependency
    logger.info("QueueManager dependency set.")

    # Initialize and Start Audio Processing Worker
    if app_state.get('tts_engine'): # Only start worker if TTS engine is available
        logger.info("Initializing AudioProcessingWorker...")
        audio_worker_logger = logging.getLogger("audio_worker")
        audio_worker_instance = AudioProcessingWorker(
            queue_manager=queue_manager_instance,
            tts_engine=app_state['tts_engine'], # Use the instance from app_state
            db_session_factory=get_db,
            logger=audio_worker_logger
        )
        audio_worker_instance.start()
        app_state['audio_worker'] = audio_worker_instance
        logger.info("AudioProcessingWorker started.")
    else:
        logger.warning("AudioProcessingWorker not started because TTSEngine failed to initialize.")
        app_state['audio_worker'] = None


    # Initialize and Start Autoplay Thread
    logger.info("Initializing and starting Autoplay Thread...")
    autoplay_logger = logging.getLogger("autoplay_loop")
    autoplay_th = threading.Thread(
        target=autoplay_loop,
        args=(get_db, queue_manager_instance, autoplay_logger),
        daemon=True # Daemon thread will exit when main program exits
    )
    autoplay_th.start()
    app_state['autoplay_thread'] = autoplay_th
    logger.info("Autoplay Thread started.")
    
    logger.info("TTS Engine, Queue Manager, Audio Worker (if TTS Engine succeeded), and Autoplay Thread initialized and started.")
    logger.info("Application startup complete.")

# 8. FastAPI Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown sequence initiated...")

    # Stop Autoplay Thread
    logger.info("Stopping Autoplay Thread...")
    autoplay_thread_stop_event.set()
    autoplay_th = app_state.get('autoplay_thread')
    if autoplay_th and autoplay_th.is_alive():
        try:
            # Wait for slightly longer than its typical wait time (cooldown or poll interval)
            # Max of these two, plus a buffer.
            join_timeout = max(settings.AUTOPLAY_COOLDOWN, settings.WORKER_POLL_INTERVAL) + 2.0
            autoplay_th.join(timeout=join_timeout)
            if autoplay_th.is_alive():
                logger.warning("Autoplay Thread did not stop in time.")
            else:
                logger.info("Autoplay Thread stopped successfully.")
        except Exception as e:
            logger.error(f"Error joining Autoplay Thread: {e}", exc_info=True)
    else:
        logger.info("Autoplay Thread was not running or not found in app_state.")

    # Stop Audio Processing Worker
    logger.info("Stopping AudioProcessingWorker...")
    audio_worker_instance = app_state.get('audio_worker')
    if audio_worker_instance:
        audio_worker_instance.stop() # stop() method handles thread joining and timeout
    else:
        logger.info("AudioProcessingWorker was not running or not found in app_state.")
        
    logger.info("Application shutdown complete.")

# 9. Static Files Mounting
# Pydantic validator in config.py (ensure_audio_output_directory_exists) already creates the directory.
# We need to make sure the path is correct for mounting.
# settings.AUDIO_OUTPUT_DIRECTORY is "tts_server/audio_files"
# If app is run from project root, this path is correct.
# The mount path "/audio" will serve files from "tts_server/audio_files" directory.
audio_dir_path = Path(settings.AUDIO_OUTPUT_DIRECTORY)
if not audio_dir_path.exists(): # Should be created by Pydantic, but double check.
    logger.warning(f"Audio output directory {audio_dir_path} not found during static mount setup. Attempting to create.")
    try:
        audio_dir_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create audio output directory {audio_dir_path} for static serving: {e}")
        # App might fail to serve audio files if this happens.

# Mount static files - ensuring directory is string for StaticFiles
# The URL path should be simple, e.g., "/audio"
app.mount("/audio", StaticFiles(directory=str(audio_dir_path)), name="audio_files")
logger.info(f"Mounted static files from '{audio_dir_path}' at '/audio'.")


# 10. API Router
app.include_router(api_router)
logger.info("API router included.")

# 11. Root Endpoint
@app.get("/")
async def root():
    return {"message": "TTS Server is running. Navigate to /docs for API documentation."}

logger.info("TTS Server application configured and ready.")

# To run with uvicorn (example, typically done from CLI):
# if __name__ == "__main__":
#     import uvicorn
#     # Use settings for host and port if defined, otherwise use uvicorn defaults
#     uvicorn_host = getattr(settings, 'TTS_SERVER_HOST', '127.0.0.1')
#     uvicorn_port = getattr(settings, 'TTS_SERVER_PORT', 8000) # Default to 8000 if not in settings for some reason
#     log_level_str = settings.LOG_LEVEL.lower() # Uvicorn expects lowercase log level
#     uvicorn.run(app, host=uvicorn_host, port=uvicorn_port, log_level=log_level_str)
