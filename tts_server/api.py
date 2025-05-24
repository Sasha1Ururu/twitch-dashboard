import logging
import os # Added os import
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Body, status as http_status
from pydantic import BaseModel, Field, field_validator # Added field_validator
from sqlalchemy.orm import Session

from .database import (
    get_db, 
    MessageStatusEnum, 
    TTSMessage, # For type hinting if needed, not directly used by all endpoints
    update_message_status # Specific function needed
)
from .queue_manager import QueueManager # This will be injected
from .config import settings

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize FastAPI router
router = APIRouter(prefix="/tts", tags=["TTS Server"])

# Module-level variable for autoplay state
autoplay_enabled: bool = False

# --- Pydantic Models ---

class AddMessagePayload(BaseModel):
    sent_by: str
    text: str
    bits_amount: Optional[int] = None
    message_type: str  # "mention" or "bits"

    @field_validator('message_type')
    def message_type_must_be_valid(cls, v):
        if v not in ['mention', 'bits']:
            raise ValueError('message_type must be "mention" or "bits"')
        return v

class SwitchQueuePayload(BaseModel):
    queue_type: str

    @field_validator('queue_type')
    def queue_type_must_be_valid(cls, v):
        if v not in ['mentions', 'bits']: # Note: QueueManager uses "mentions" (plural)
            raise ValueError('queue_type must be "mentions" or "bits"')
        return v

class QueueStatsResponse(BaseModel):
    active_queue_type: str # Corrected from active_queue to match QueueManager's stats
    pending_count: int
    ready_count: int
    mentions_total_audio_size_bytes: int
    autoplay_enabled: bool
    # Added from QueueManager stats for completeness, can be culled if not needed by client
    error_count: int
    processing_count: int


class PlayNextResponse(BaseModel):
    message_id: Optional[int] = None
    sent_by: Optional[str] = None
    text: Optional[str] = None
    audio_file_path: Optional[str] = None # Server-side path

class BasicConfigResponse(BaseModel):
    voice_config: str
    autoplay_cooldown: int
    tts_speed: float
    lang_code: str
    kokoro_lang_code: str


# --- Dependency Injection Placeholder ---

# This placeholder will be replaced by actual dependency injection in main.py
# For now, it allows the API endpoints to declare the dependency.
# The actual QueueManager instance will be created in main.py and passed.
def get_queue_manager() -> QueueManager:
    # This function should be overridden by FastAPI's dependency injection in main.py
    # to provide the actual QueueManager instance.
    # logger.critical("get_queue_manager placeholder was called! This should be overridden by FastAPI DI.")
    raise NotImplementedError("QueueManager dependency not configured. This should be injected by FastAPI.")

# --- API Endpoints ---

@router.post("/add_message", status_code=http_status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def add_tts_message(
    payload: AddMessagePayload,
    qm: QueueManager = Depends(get_queue_manager) # Placeholder dependency
):
    logger.info(f"Received /add_message request for type '{payload.message_type}' from '{payload.sent_by}'.")
    
    # message_type validation is now handled by Pydantic model

    message_data = {
        "sent_by": payload.sent_by,
        "text": payload.text,
        "bits_amount": payload.bits_amount,
        "message_type": payload.message_type, # "mention" or "bits"
        "status": MessageStatusEnum.PENDING # Default status for new messages
    }

    try:
        created_message = qm.add_message_to_queue(message_data)
        if not created_message:
            logger.error(f"Failed to add message to queue. Payload: {payload.dict()}")
            raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add message to queue.")
        
        logger.info(f"Message ID {created_message.id} added to '{payload.message_type}' queue.")
        return {"message": "Message added to queue", "message_id": created_message.id}
    except NotImplementedError: # Catch if get_queue_manager is not overridden
        logger.critical("QueueManager dependency not available for /add_message.")
        raise HTTPException(status_code=http_status.HTTP_501_NOT_IMPLEMENTED, detail="Server configuration error: QueueManager not available.")
    except Exception as e:
        logger.error(f"Error in /add_message: {e}", exc_info=True)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/active_queue_stats", response_model=QueueStatsResponse)
async def get_active_queue_statistics(
    qm: QueueManager = Depends(get_queue_manager)
):
    global autoplay_enabled
    logger.info("Received /active_queue_stats request.")
    try:
        stats = qm.get_active_queue_stats() # This is already a dict
        # Ensure all fields expected by QueueStatsResponse are in 'stats' or add them
        # QueueManager.get_active_queue_stats returns:
        # active_queue_type, pending_count, ready_count, mentions_total_audio_size_bytes, error_count, processing_count
        
        # Add autoplay_enabled to the response
        stats_response_data = {**stats, "autoplay_enabled": autoplay_enabled}
        
        return QueueStatsResponse(**stats_response_data)
    except NotImplementedError:
        logger.critical("QueueManager dependency not available for /active_queue_stats.")
        raise HTTPException(status_code=http_status.HTTP_501_NOT_IMPLEMENTED, detail="Server configuration error: QueueManager not available.")
    except Exception as e:
        logger.error(f"Error in /active_queue_stats: {e}", exc_info=True)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/play_next", response_model=PlayNextResponse)
async def play_next_message(
    db: Session = Depends(get_db),
    qm: QueueManager = Depends(get_queue_manager)
):
    logger.info("Received /play_next request.")
    try:
        message_to_play = qm.get_next_message_to_play()

        if message_to_play:
            logger.info(f"Message ID {message_to_play.id} selected to play from '{qm.active_queue_type}' queue.")
            updated_msg = update_message_status(
                db, 
                message_id=message_to_play.id, 
                new_status=MessageStatusEnum.PLAYING,
                played_at=datetime.utcnow() # Playback started
            )
            if not updated_msg:
                # This case should be rare if get_next_message_to_play returned a message
                logger.error(f"Failed to update status to PLAYING for message ID {message_to_play.id}.")
                # Consider how to handle this - maybe return empty or raise error
                # For now, proceed with returning data but log it as an inconsistency
            
            # Construct server-relative audio URL if needed, or return raw path
            # Assuming AUDIO_OUTPUT_DIRECTORY = "tts_server/audio_files"
            # and static files are mounted at "/audio" for "tts_server/audio_files"
            # Then, audio_file_path from DB is like "tts_server/audio_files/message_123.wav"
            # Client-accessible URL would be "/audio/message_123.wav"
            
            relative_audio_path = None
            if message_to_play.audio_path:
                # Ensure AUDIO_OUTPUT_DIRECTORY ends with a slash for safe replacement
                # Or use os.path.relpath if paths are guaranteed to be well-formed
                base_path_to_strip = settings.AUDIO_OUTPUT_DIRECTORY
                if not base_path_to_strip.endswith(os.path.sep):
                    base_path_to_strip += os.path.sep
                
                if message_to_play.audio_path.startswith(base_path_to_strip):
                    file_name = message_to_play.audio_path[len(base_path_to_strip):]
                    relative_audio_path = f"/audio/{file_name}" # Assuming /audio is static mount point
                else: # Path is not relative to expected output dir, return as is or log warning
                    logger.warning(f"Audio path {message_to_play.audio_path} for msg {message_to_play.id} is not in expected base dir {base_path_to_strip}. Returning raw path.")
                    relative_audio_path = message_to_play.audio_path # Fallback or adjust as needed

            return PlayNextResponse(
                message_id=message_to_play.id,
                sent_by=message_to_play.sent_by,
                text=message_to_play.text,
                audio_file_path=relative_audio_path # Use the constructed relative path
            )
        else:
            logger.info("No message available to play from the active queue.")
            return PlayNextResponse() # All fields None
    except NotImplementedError:
        logger.critical("QueueManager dependency not available for /play_next.")
        raise HTTPException(status_code=http_status.HTTP_501_NOT_IMPLEMENTED, detail="Server configuration error: QueueManager not available.")
    except Exception as e:
        logger.error(f"Error in /play_next: {e}", exc_info=True)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/mark_played/{message_id}", status_code=http_status.HTTP_200_OK, response_model=Dict[str, Any])
async def mark_message_as_played(
    message_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"Received /mark_played request for message ID {message_id}.")
    try:
        # Ensure played_at is also updated if not already set by /play_next logic for starting playback
        # This endpoint explicitly means playback *finished*.
        # The `update_message_status` can take kwargs.
        # If `played_at` was set on PLAYING, this just sets status to PLAYED.
        # If we want `played_at` to mean "finished playing", then set it here.
        # Let's assume `played_at` is "playback started time" for now.
        updated_message = update_message_status(
            db, 
            message_id=message_id, 
            new_status=MessageStatusEnum.PLAYED
            # Optionally add/update a `playback_finished_at=datetime.utcnow()` field if model supports it
        )

        if not updated_message:
            logger.warning(f"Message ID {message_id} not found or no status change needed for /mark_played.")
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Message not found or status could not be updated.")
        
        logger.info(f"Message ID {message_id} marked as PLAYED.")
        return {"message": "Message marked as played", "message_id": message_id}
    except Exception as e:
        logger.error(f"Error in /mark_played/{message_id}: {e}", exc_info=True)
        # Check if it's an HTTPException from a previous step (like the 404)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/autoplay/start", status_code=http_status.HTTP_200_OK, response_model=Dict[str, str])
async def start_autoplay():
    global autoplay_enabled
    autoplay_enabled = True
    logger.info("Autoplay started via API request.")
    return {"message": "Autoplay started"}

@router.post("/autoplay/stop", status_code=http_status.HTTP_200_OK, response_model=Dict[str, str])
async def stop_autoplay():
    global autoplay_enabled
    autoplay_enabled = False
    logger.info("Autoplay stopped via API request.")
    return {"message": "Autoplay stopped"}

@router.post("/clear_active_queue", status_code=http_status.HTTP_200_OK, response_model=Dict[str, str])
async def clear_tts_active_queue(
    qm: QueueManager = Depends(get_queue_manager)
):
    logger.info(f"Received /clear_active_queue request for queue '{qm.active_queue_type if qm else 'Unknown'}'.")
    try:
        active_queue_type_before_clear = qm.active_queue_type # Store before potential modification by clear
        cleared_count = qm.clear_active_queue()
        logger.info(f"{cleared_count} messages cleared from '{active_queue_type_before_clear}' queue.")
        return {"message": f"Active queue ({active_queue_type_before_clear}) cleared. {cleared_count} messages marked as deleted."}
    except NotImplementedError:
        logger.critical("QueueManager dependency not available for /clear_active_queue.")
        raise HTTPException(status_code=http_status.HTTP_501_NOT_IMPLEMENTED, detail="Server configuration error: QueueManager not available.")
    except Exception as e:
        logger.error(f"Error in /clear_active_queue: {e}", exc_info=True)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/switch_active_queue", status_code=http_status.HTTP_200_OK, response_model=Dict[str, str])
async def switch_tts_active_queue(
    payload: SwitchQueuePayload,
    qm: QueueManager = Depends(get_queue_manager)
):
    logger.info(f"Received /switch_active_queue request to '{payload.queue_type}'.")
    # Validation of queue_type is handled by Pydantic model
    try:
        switched = qm.switch_active_queue(payload.queue_type)
        if switched:
            logger.info(f"Active queue successfully switched to '{payload.queue_type}'.")
            return {"message": f"Active queue switched to {payload.queue_type}"}
        else:
            # This could mean it's already the active queue or an invalid type (though Pydantic should catch invalid type)
            logger.warning(f"Failed to switch queue to '{payload.queue_type}'. It might be already active or an issue occurred.")
            # QueueManager.switch_active_queue returns False if already active or invalid.
            # Pydantic validator for SwitchQueuePayload already ensures type is 'mentions' or 'bits'.
            # So, if False, it's likely because it's already the active queue.
            current_active = qm.active_queue_type
            if payload.queue_type == current_active:
                 return {"message": f"Queue '{payload.queue_type}' is already active. No change made."}
            else: # Should not happen if Pydantic validator works and QM logic is sound.
                 raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=f"Could not switch to queue '{payload.queue_type}'.")

    except NotImplementedError:
        logger.critical("QueueManager dependency not available for /switch_active_queue.")
        raise HTTPException(status_code=http_status.HTTP_501_NOT_IMPLEMENTED, detail="Server configuration error: QueueManager not available.")
    except Exception as e: # Catch-all for other unexpected errors
        logger.error(f"Error in /switch_active_queue: {e}", exc_info=True)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/config", response_model=BasicConfigResponse)
async def get_basic_config():
    logger.info("Received /config request.")
    try:
        return BasicConfigResponse(
            voice_config=settings.VOICE_CONFIG_STR,
            autoplay_cooldown=settings.AUTOPLAY_COOLDOWN,
            tts_speed=settings.TTS_ENGINE_SPEED,
            lang_code=settings.LANG_CODE,
            kokoro_lang_code=settings.KOKORO_LANG_CODE
        )
    except Exception as e:
        logger.error(f"Error in /config: {e}", exc_info=True)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Redundant imports removed from here (os, validator)
# os was moved to top, validator replaced by field_validator
