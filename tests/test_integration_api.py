import pytest
import time
import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Assuming conftest.py provides these fixtures:
# test_client, test_db_session_factory, mock_audio_output_dir, mock_tts_synthesize

from tts_server.database import TTSMessage, MessageStatusEnum # For DB assertions
from tts_server.config import settings # For WORKER_POLL_INTERVAL, MENTIONS_QUEUE_MAX_AUDIO_BYTES


# Helper function
def get_message_from_db(session: Session, message_id: int) -> TTSMessage | None:
    """Fetches a TTSMessage by ID from the database."""
    return session.query(TTSMessage).filter(TTSMessage.id == message_id).first()


# --- Test Scenarios ---

# 1. Test Full Message Lifecycle
def test_full_message_lifecycle(
    test_client: TestClient, 
    test_db_session_factory, # Note: fixture name in conftest.py is test_db_session_factory
    mock_tts_synthesize, # Fixture from conftest.py
    mock_audio_output_dir # Fixture from conftest.py
):
    # Add Message
    add_payload = {
        "sent_by": "test_user_lifecycle",
        "text": "Hello, this is a lifecycle test.",
        "bits_amount": 100,
        "message_type": "bits"
    }
    response = test_client.post("/tts/add_message", json=add_payload) # Corrected prefix
    assert response.status_code == 201 # Created
    message_id = response.json()["message_id"]
    assert isinstance(message_id, int)

    # Verify Pending
    with test_db_session_factory() as session:
        message = get_message_from_db(session, message_id)
        assert message is not None
        assert message.status == MessageStatusEnum.PENDING

    # Simulate Worker Processing
    # Wait for worker to pick up and "synthesize"
    time.sleep(settings.WORKER_POLL_INTERVAL * 2 + 0.5) 

    # Verify Ready
    generated_audio_path = ""
    with test_db_session_factory() as session:
        message = get_message_from_db(session, message_id)
        assert message is not None
        assert message.status == MessageStatusEnum.READY
        assert message.audio_path is not None
        assert message.audio_size_bytes is not None
        assert message.audio_size_bytes > 0
        generated_audio_path = message.audio_path # Store for later check
        assert os.path.exists(generated_audio_path), f"Dummy audio file {generated_audio_path} should exist."
        # Ensure it's in the mock_audio_output_dir
        assert str(Path(mock_audio_output_dir)) in generated_audio_path

    # Play Next
    response = test_client.post("/tts/play_next") # Corrected prefix
    assert response.status_code == 200
    play_next_data = response.json()
    assert play_next_data["message_id"] == message_id
    assert play_next_data["audio_file_path"] is not None # This is the client-facing path

    # Verify Playing
    with test_db_session_factory() as session:
        message = get_message_from_db(session, message_id)
        assert message is not None
        assert message.status == MessageStatusEnum.PLAYING

    # Mark Played
    response = test_client.post(f"/tts/mark_played/{message_id}") # Corrected prefix
    assert response.status_code == 200

    # Verify Played
    with test_db_session_factory() as session:
        message = get_message_from_db(session, message_id)
        assert message is not None
        assert message.status == MessageStatusEnum.PLAYED
    
    # Assert dummy audio file still exists (marking played doesn't delete)
    assert os.path.exists(generated_audio_path), f"Dummy audio file {generated_audio_path} should still exist after playing."


# 2. Test Queue Management
def test_switch_queue_and_play(
    test_client: TestClient, 
    test_db_session_factory,
    mock_tts_synthesize,
    mock_audio_output_dir
):
    # Add a "mention" message
    mention_payload = {"sent_by": "user_mention", "text": "Mention test", "message_type": "mentions"}
    response_m = test_client.post("/tts/add_message", json=mention_payload) # Corrected prefix
    assert response_m.status_code == 201
    message_id_mention = response_m.json()["message_id"]

    # Add a "bits" message
    bits_payload = {"sent_by": "user_bits", "text": "Bits test", "message_type": "bits", "bits_amount": 50}
    response_b = test_client.post("/tts/add_message", json=bits_payload) # Corrected prefix
    assert response_b.status_code == 201
    message_id_bits = response_b.json()["message_id"]

    # Wait for processing (both messages)
    time.sleep(settings.WORKER_POLL_INTERVAL * 3 + 0.5) # Longer wait for potentially two items

    # Initially active queue is "mentions" (default in QueueManager)
    # Verify by checking stats or by playing next
    stats_response = test_client.get("/tts/active_queue_stats") # Corrected prefix
    assert stats_response.json()["active_queue_type"] == "mentions"
    
    response_play_mention = test_client.post("/tts/play_next") # Corrected prefix
    assert response_play_mention.status_code == 200
    assert response_play_mention.json()["message_id"] == message_id_mention
    test_client.post(f"/tts/mark_played/{message_id_mention}") # Corrected prefix

    # Switch to "bits" queue
    switch_payload = {"queue_type": "bits"}
    response_switch = test_client.post("/tts/switch_active_queue", json=switch_payload) # Corrected prefix
    assert response_switch.status_code == 200

    # Verify active queue is "bits"
    stats_response_after_switch = test_client.get("/tts/active_queue_stats") # Corrected prefix
    assert stats_response_after_switch.json()["active_queue_type"] == "bits"

    # Play next from "bits" queue
    response_play_bits = test_client.post("/tts/play_next") # Corrected prefix
    assert response_play_bits.status_code == 200
    assert response_play_bits.json()["message_id"] == message_id_bits
    test_client.post(f"/tts/mark_played/{message_id_bits}") # Corrected prefix


def test_clear_active_queue(
    test_client: TestClient, 
    test_db_session_factory,
    mock_tts_synthesize, # Needed for messages to become READY/PENDING
    mock_audio_output_dir
):
    # Add a "mention" message (m1) and let it become READY
    m1_payload = {"sent_by": "user_m1", "text": "Mention to be cleared 1 (ready)", "message_type": "mentions"}
    response_m1 = test_client.post("/tts/add_message", json=m1_payload) # Corrected prefix
    assert response_m1.status_code == 201
    m1_id = response_m1.json()["message_id"]
    
    time.sleep(settings.WORKER_POLL_INTERVAL * 2 + 0.5) # Allow m1 to become READY
    
    m1_audio_path = ""
    with test_db_session_factory() as session:
        m1_msg = get_message_from_db(session, m1_id)
        assert m1_msg.status == MessageStatusEnum.READY
        m1_audio_path = m1_msg.audio_path
        assert os.path.exists(m1_audio_path)

    # Add another "mention" message (m2), keep it PENDING (don't wait for worker)
    m2_payload = {"sent_by": "user_m2", "text": "Mention to be cleared 2 (pending)", "message_type": "mentions"}
    response_m2 = test_client.post("/tts/add_message", json=m2_payload) # Corrected prefix
    assert response_m2.status_code == 201
    m2_id = response_m2.json()["message_id"]

    # Clear active queue ("mentions" is default)
    response_clear = test_client.post("/tts/clear_active_queue") # Corrected prefix
    assert response_clear.status_code == 200
    assert "messages marked as deleted" in response_clear.json()["message"]

    # Verify m1 and m2 status is DELETED in DB
    with test_db_session_factory() as session:
        m1_msg_after_clear = get_message_from_db(session, m1_id)
        m2_msg_after_clear = get_message_from_db(session, m2_id)
        assert m1_msg_after_clear.status == MessageStatusEnum.DELETED
        assert m2_msg_after_clear.status == MessageStatusEnum.DELETED

    # Allow worker to handle deletions of audio files
    time.sleep(settings.WORKER_POLL_INTERVAL * 2 + 0.5) 

    # Verify dummy audio file for m1 (the READY one) is deleted
    assert not os.path.exists(m1_audio_path), f"Audio file {m1_audio_path} for m1 should be deleted."


# 3. Test Mentions Queue Overflow
def test_mentions_queue_overflow(
    test_client: TestClient, 
    test_db_session_factory,
    mock_tts_synthesize, # We will configure its side_effect for this test
    mock_audio_output_dir
):
    # Configure mock_tts_synthesize to return specific large sizes
    # MENTIONS_QUEUE_MAX_AUDIO_BYTES is 200MB in QueueManager
    # If settings object has it, use that, otherwise assume QueueManager's default.
    # For this test, let's rely on QueueManager's default.
    # queue_manager.MENTIONS_QUEUE_MAX_AUDIO_BYTES = 200 * 1024 * 1024
    
    large_audio_size = 70 * 1024 * 1024  # 70MB
    
    created_files = {} # To store paths of created dummy files

    def large_size_synthesize_effect(message_id, text_to_synthesize, output_directory):
        filename = f"message_{message_id}_test_large.wav"
        filepath = Path(output_directory) / filename
        with open(filepath, 'w') as f:
            f.write("dummy large audio content") # Actual content size doesn't matter for this mock
        
        # Store path for cleanup or verification if needed
        created_files[message_id] = str(filepath)
        return str(filepath), large_audio_size # Return the large size

    mock_tts_synthesize.side_effect = large_size_synthesize_effect

    # Add 3 "mention" messages (msg1, msg2, msg3) - total 210MB, should overflow
    msg_ids = []
    for i in range(1, 4): # msg1, msg2, msg3
        payload = {"sent_by": f"user_overflow_{i}", "text": f"Overflow test msg {i}", "message_type": "mentions"}
        response = test_client.post("/tts/add_message", json=payload) # Corrected prefix
        assert response.status_code == 201
        msg_ids.append(response.json()["message_id"])

    # Wait for them to process to READY. Overflow logic happens on ADD.
    # The third add should trigger overflow and delete the first one.
    time.sleep(settings.WORKER_POLL_INTERVAL * (len(msg_ids) * 2) + 1.0) # Generous wait

    # Verify in DB: msg1 status is DELETED, msg2 and msg3 are READY
    with test_db_session_factory() as session:
        msg1 = get_message_from_db(session, msg_ids[0])
        msg2 = get_message_from_db(session, msg_ids[1])
        msg3 = get_message_from_db(session, msg_ids[2])
        
        assert msg1.status == MessageStatusEnum.DELETED, f"Msg1 (id: {msg_ids[0]}) should be DELETED due to overflow."
        assert msg2.status == MessageStatusEnum.READY, f"Msg2 (id: {msg_ids[1]}) should be READY."
        assert msg3.status == MessageStatusEnum.READY, f"Msg3 (id: {msg_ids[2]}) should be READY."

    # Verify dummy audio file for msg1 is deleted (by worker cleanup of DELETED)
    # Files for msg2, msg3 exist.
    time.sleep(settings.WORKER_POLL_INTERVAL * 2 + 0.5) # Allow worker to clean DELETED files
    assert not os.path.exists(created_files[msg_ids[0]]), f"Audio for msg1 (id: {msg_ids[0]}) should be deleted."
    assert os.path.exists(created_files[msg_ids[1]]), f"Audio for msg2 (id: {msg_ids[1]}) should exist."
    assert os.path.exists(created_files[msg_ids[2]]), f"Audio for msg3 (id: {msg_ids[2]}) should exist."

    # Add a 4th "mention" message (msg4). This should cause msg2 to be deleted.
    payload_msg4 = {"sent_by": "user_overflow_4", "text": "Overflow test msg 4", "message_type": "mentions"}
    response_msg4 = test_client.post("/tts/add_message", json=payload_msg4) # Corrected prefix
    assert response_msg4.status_code == 201
    msg4_id = response_msg4.json()["message_id"]
    
    time.sleep(settings.WORKER_POLL_INTERVAL * 2 + 0.5) # Wait for msg4 processing & overflow

    # Verify msg2 is now DELETED, msg3 and msg4 are READY
    with test_db_session_factory() as session:
        msg1_final = get_message_from_db(session, msg_ids[0]) # Should still be DELETED
        msg2_final = get_message_from_db(session, msg_ids[1])
        msg3_final = get_message_from_db(session, msg_ids[2])
        msg4_final = get_message_from_db(session, msg4_id)

        assert msg1_final.status == MessageStatusEnum.DELETED
        assert msg2_final.status == MessageStatusEnum.DELETED, f"Msg2 (id: {msg_ids[1]}) should now be DELETED."
        assert msg3_final.status == MessageStatusEnum.READY, f"Msg3 (id: {msg_ids[2]}) should be READY."
        assert msg4_final.status == MessageStatusEnum.READY, f"Msg4 (id: {msg4_id}) should be READY."

    # Worker cleanup for msg2's audio file
    time.sleep(settings.WORKER_POLL_INTERVAL * 2 + 0.5)
    assert not os.path.exists(created_files[msg_ids[1]]), f"Audio for msg2 (id: {msg_ids[1]}) should be deleted."
    assert os.path.exists(created_files[msg_ids[2]]), f"Audio for msg3 (id: {msg_ids[2]}) should still exist."
    assert os.path.exists(created_files[msg4_id]), f"Audio for msg4 (id: {msg4_id}) should exist."


# 4. Test Autoplay Flags
def test_autoplay_flags(test_client: TestClient):
    # Check initial state (optional, depends on how API initializes it, default in api.py is False)
    stats_initial = test_client.get("/tts/active_queue_stats").json() # Corrected prefix
    assert stats_initial["autoplay_enabled"] is False 

    # Start Autoplay
    response_start = test_client.post("/tts/autoplay/start") # Corrected prefix
    assert response_start.status_code == 200
    stats_after_start = test_client.get("/tts/active_queue_stats").json() # Corrected prefix
    assert stats_after_start["autoplay_enabled"] is True

    # Stop Autoplay
    response_stop = test_client.post("/tts/autoplay/stop") # Corrected prefix
    assert response_stop.status_code == 200
    stats_after_stop = test_client.get("/tts/active_queue_stats").json() # Corrected prefix
    assert stats_after_stop["autoplay_enabled"] is False


# 5. Test Error Handling
def test_add_message_invalid_payload(test_client: TestClient):
    # Empty text
    invalid_payload_empty_text = {"sent_by": "test_user", "text": "", "message_type": "mention"}
    # Pydantic model in api.py for AddMessagePayload doesn't explicitly forbid empty text,
    # but the API endpoint in previous versions did. Let's assume Pydantic doesn't stop it.
    # The current AddMessagePayload in api.py doesn't have a validator for non-empty text.
    # So this might result in 201 if not for DB constraints or other logic.
    # However, the API endpoint in `tts_server/api.py` had:
    # `if not payload.text.strip(): raise HTTPException(...)` which is now removed.
    # Let's assume the Pydantic model is the source of truth for validation here.
    # If the model allows empty text, this would be 201.
    # For now, let's test based on the Pydantic validator for message_type.
    
    # Invalid message_type
    invalid_payload_type = {"sent_by": "test_user", "text": "Valid text", "message_type": "invalid_type"}
    response = test_client.post("/tts/add_message", json=invalid_payload_type) # Corrected prefix
    assert response.status_code == 422 # Unprocessable Entity due to Pydantic validation
    assert "message_type must be \"mention\" or \"bits\"" in response.text


def test_mark_played_non_existent(test_client: TestClient):
    response = test_client.post("/tts/mark_played/999999") # Non-existent ID. Corrected prefix.
    assert response.status_code == 404 # Not Found


def test_synthesis_error(
    test_client: TestClient, 
    test_db_session_factory,
    mock_tts_synthesize # We will configure its side_effect
):
    # Configure mock_tts_synthesize to raise an Exception
    mock_tts_synthesize.side_effect = Exception("Simulated TTS Synthesis Error")

    add_payload = {"sent_by": "test_user_synth_error", "text": "This will fail synthesis", "message_type": "bits"}
    response = test_client.post("/tts/add_message", json=add_payload) # Corrected prefix
    assert response.status_code == 201
    message_id = response.json()["message_id"]

    # Wait for worker to attempt processing
    time.sleep(settings.WORKER_POLL_INTERVAL * 2 + 0.5)

    # Verify message status in DB is ERROR
    with test_db_session_factory() as session:
        message = get_message_from_db(session, message_id)
        assert message is not None
        assert message.status == MessageStatusEnum.ERROR, "Message status should be ERROR after synthesis failure."

if __name__ == "__main__":
    # This allows running pytest directly on this file if needed
    # pytest.main([__file__])
    # However, it's better to run pytest from the project root: `pytest tests/`
    pass
