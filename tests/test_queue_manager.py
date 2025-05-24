import pytest
from unittest.mock import MagicMock, patch, call # call for checking multiple calls if needed

# Import the class to be tested
from tts_server.queue_manager import QueueManager
# Import related items that might be needed for mocks or type checking
from tts_server.database import TTSMessage, MessageStatusEnum 

@pytest.fixture
def mock_db_session():
    """Provides a mock database session."""
    session = MagicMock()
    # Configure specific query results if needed per test, or here for general cases
    # session.query.return_value.filter.return_value.first.return_value = None # Example
    return session

@pytest.fixture
def mock_db_session_factory(mock_db_session):
    """Provides a mock database session factory that returns the mock_db_session."""
    # The factory should behave as a context manager if used with 'with ... as db:'
    factory = MagicMock()
    
    # To make it work with 'with db_session_factory() as db:'
    # The factory itself doesn't need to be a context manager, 
    # but the object it *returns* (the session) might be used as one by SQLAlchemy,
    # or directly as in the QueueManager.
    # QueueManager uses: `with self.db_session_factory() as db:`
    # So, the factory's __call__ should return an object that is a context manager.
    
    mock_context_manager = MagicMock()
    mock_context_manager.__enter__.return_value = mock_db_session # This is 'db'
    mock_context_manager.__exit__.return_value = None # Typically returns None or False

    factory.return_value = mock_context_manager # factory() now returns the context manager
    return factory


@pytest.fixture
def mock_logger():
    """Provides a mock logger."""
    return MagicMock()

@pytest.fixture
def queue_manager_instance(mock_db_session_factory, mock_logger):
    """Provides an instance of QueueManager with mocked dependencies."""
    return QueueManager(db_session_factory=mock_db_session_factory, logger=mock_logger)

# --- Mocks for database functions ---
# These will be patched where QueueManager uses them.

@patch('tts_server.queue_manager.add_message')
def test_add_message_to_queue_bits(mock_add_message_db, queue_manager_instance, mock_db_session):
    """Test adding a message to the 'bits' queue (no overflow logic)."""
    message_data = {"message_type": "bits", "text": "Test bits message", "sent_by": "user1"}
    mock_created_message = TTSMessage(id=1, **message_data) # Simulate a created message
    mock_add_message_db.return_value = mock_created_message

    created_msg_obj = queue_manager_instance.add_message_to_queue(message_data)

    # db_session_factory() is called, then its __enter__ yields mock_db_session
    # So, add_message should be called with mock_db_session
    mock_add_message_db.assert_called_once_with(mock_db_session, message_data)
    assert created_msg_obj is not None
    assert created_msg_obj.id == 1
    queue_manager_instance.logger.info.assert_any_call(
        f"Message ID {mock_created_message.id} (type: bits) added to DB with status PENDING."
    )


@patch('tts_server.queue_manager.mark_messages_as_deleted')
@patch('tts_server.queue_manager.get_messages_to_delete_for_overflow')
@patch('tts_server.queue_manager.get_total_audio_size')
@patch('tts_server.queue_manager.add_message')
def test_add_message_to_queue_mentions_no_overflow(
    mock_add_message_db, mock_get_total_audio_size_db, 
    mock_get_msg_to_delete_db, mock_mark_deleted_db,
    queue_manager_instance, mock_db_session):
    """Test adding to 'mentions' queue without overflow."""
    message_data = {"message_type": "mentions", "text": "Test mention", "sent_by": "user2"}
    mock_created_message = TTSMessage(id=2, **message_data)
    mock_add_message_db.return_value = mock_created_message
    
    # Simulate no overflow: total size is less than max
    mock_get_total_audio_size_db.return_value = 100 * 1024 * 1024 # 100MB

    created_msg_obj = queue_manager_instance.add_message_to_queue(message_data)

    mock_add_message_db.assert_called_once_with(mock_db_session, message_data)
    mock_get_total_audio_size_db.assert_called_once_with(mock_db_session, queue_type="mentions")
    mock_get_msg_to_delete_db.assert_not_called() # Should not be called if no overflow
    mock_mark_deleted_db.assert_not_called()
    assert created_msg_obj is not None
    assert created_msg_obj.id == 2

@patch('tts_server.queue_manager.mark_messages_as_deleted')
@patch('tts_server.queue_manager.get_messages_to_delete_for_overflow')
@patch('tts_server.queue_manager.get_total_audio_size')
@patch('tts_server.queue_manager.add_message')
def test_add_message_to_queue_mentions_with_overflow(
    mock_add_message_db, mock_get_total_audio_size_db, 
    mock_get_msg_to_delete_db, mock_mark_deleted_db,
    queue_manager_instance, mock_db_session):
    """Test adding to 'mentions' queue with overflow, triggering deletions."""
    message_data = {"message_type": "mentions", "text": "Another mention", "sent_by": "user3"}
    mock_created_message = TTSMessage(id=3, **message_data)
    mock_add_message_db.return_value = mock_created_message

    # Simulate overflow: total size is more than max (default 200MB for QM)
    # QM's MENTIONS_QUEUE_MAX_AUDIO_BYTES is 200 * 1024 * 1024
    current_size_simulated = 250 * 1024 * 1024 # 250MB
    mock_get_total_audio_size_db.return_value = current_size_simulated 
    
    # Simulate messages to be deleted
    mock_msg_to_delete1 = TTSMessage(id=101, message_type="mentions", audio_size_bytes=30*1024*1024)
    mock_msg_to_delete2 = TTSMessage(id=102, message_type="mentions", audio_size_bytes=30*1024*1024)
    mock_get_msg_to_delete_db.return_value = [mock_msg_to_delete1, mock_msg_to_delete2]

    mock_mark_deleted_db.return_value = 2 # Simulate 2 messages marked as deleted

    created_msg_obj = queue_manager_instance.add_message_to_queue(message_data)

    mock_add_message_db.assert_called_once_with(mock_db_session, message_data)
    mock_get_total_audio_size_db.assert_called_once_with(mock_db_session, queue_type="mentions")
    
    expected_size_to_free = current_size_simulated - queue_manager_instance.MENTIONS_QUEUE_MAX_AUDIO_BYTES
    mock_get_msg_to_delete_db.assert_called_once_with(mock_db_session, queue_type="mentions", size_to_free=expected_size_to_free)
    mock_mark_deleted_db.assert_called_once_with(mock_db_session, message_ids=[101, 102])
    
    assert created_msg_obj is not None
    assert created_msg_obj.id == 3
    queue_manager_instance.logger.info.assert_any_call("2 messages marked as DELETED due to overflow.")


def test_switch_active_queue(queue_manager_instance):
    """Test switching the active queue type."""
    assert queue_manager_instance.active_queue_type == "mentions" # Default

    switched_to_bits = queue_manager_instance.switch_active_queue("bits")
    assert switched_to_bits is True
    assert queue_manager_instance.active_queue_type == "bits"
    queue_manager_instance.logger.info.assert_any_call("Active queue switched to 'bits'.")

    switched_to_mentions = queue_manager_instance.switch_active_queue("mentions")
    assert switched_to_mentions is True
    assert queue_manager_instance.active_queue_type == "mentions"

    # Try switching to an invalid type
    switched_invalid = queue_manager_instance.switch_active_queue("invalid_type")
    assert switched_invalid is False
    assert queue_manager_instance.active_queue_type == "mentions" # Should not change
    queue_manager_instance.logger.warning.assert_any_call("Invalid queue type for switch: 'invalid_type'. Must be 'mentions' or 'bits'.")

    # Try switching to the already active type
    switched_same = queue_manager_instance.switch_active_queue("mentions")
    assert switched_same is False # As per current QM logic
    assert queue_manager_instance.active_queue_type == "mentions"


@patch('tts_server.queue_manager.mark_messages_as_deleted')
@patch('tts_server.queue_manager.get_messages_by_status')
def test_clear_active_queue(mock_get_messages_db, mock_mark_deleted_db, 
                            queue_manager_instance, mock_db_session):
    """Test clearing the active queue."""
    # Simulate some PENDING and READY messages
    mock_pending_msg1 = TTSMessage(id=201, status=MessageStatusEnum.PENDING)
    mock_ready_msg1 = TTSMessage(id=202, status=MessageStatusEnum.READY)
    
    # Configure get_messages_by_status to return different lists based on status
    def get_messages_side_effect(db, status, queue_type, limit):
        if status == MessageStatusEnum.PENDING:
            return [mock_pending_msg1]
        elif status == MessageStatusEnum.READY:
            return [mock_ready_msg1]
        return []
    mock_get_messages_db.side_effect = get_messages_side_effect
    
    mock_mark_deleted_db.return_value = 2 # Simulate 2 messages deleted

    # Active queue is 'mentions' by default
    cleared_count = queue_manager_instance.clear_active_queue()

    # Check calls to get_messages_by_status
    # call(mock_db_session, status=MessageStatusEnum.PENDING, queue_type="mentions", limit=-1)
    # call(mock_db_session, status=MessageStatusEnum.READY, queue_type="mentions", limit=-1)
    # Using any_order because the order of these two specific calls doesn't strictly matter for the outcome.
    mock_get_messages_db.assert_has_calls([
        call(mock_db_session, status=MessageStatusEnum.PENDING, queue_type="mentions", limit=-1),
        call(mock_db_session, status=MessageStatusEnum.READY, queue_type="mentions", limit=-1)
    ], any_order=True)
    
    # Check that mark_messages_as_deleted was called with the IDs of these messages
    mock_mark_deleted_db.assert_called_once_with(mock_db_session, message_ids=[201, 202])
    assert cleared_count == 2
    queue_manager_instance.logger.info.assert_any_call("Successfully marked 2 messages as DELETED from 'mentions' queue.")


@patch('tts_server.queue_manager.get_oldest_message_for_processing')
def test_get_next_message_to_process(mock_get_oldest_pending_db, queue_manager_instance, mock_db_session):
    """Test getting the next message to process."""
    mock_message = TTSMessage(id=301, status=MessageStatusEnum.PENDING, message_type="mentions")
    mock_get_oldest_pending_db.return_value = mock_message

    # Default active queue is "mentions"
    next_msg = queue_manager_instance.get_next_message_to_process()

    mock_get_oldest_pending_db.assert_called_once_with(mock_db_session, queue_type="mentions")
    assert next_msg is mock_message
    queue_manager_instance.logger.info.assert_any_call(
        f"Found PENDING message ID {mock_message.id} in 'mentions' queue to process."
    )

    # Test with a different active queue
    queue_manager_instance.switch_active_queue("bits")
    mock_get_oldest_pending_db.reset_mock() # Reset for the next call
    mock_message_bits = TTSMessage(id=302, status=MessageStatusEnum.PENDING, message_type="bits")
    mock_get_oldest_pending_db.return_value = mock_message_bits
    
    next_msg_bits = queue_manager_instance.get_next_message_to_process()
    mock_get_oldest_pending_db.assert_called_once_with(mock_db_session, queue_type="bits")
    assert next_msg_bits is mock_message_bits


@patch('tts_server.queue_manager.get_oldest_ready_message')
def test_get_next_message_to_play(mock_get_oldest_ready_db, queue_manager_instance, mock_db_session):
    """Test getting the next message to play."""
    mock_message = TTSMessage(id=401, status=MessageStatusEnum.READY, message_type="mentions")
    mock_get_oldest_ready_db.return_value = mock_message

    next_msg = queue_manager_instance.get_next_message_to_play()

    mock_get_oldest_ready_db.assert_called_once_with(mock_db_session, queue_type="mentions")
    assert next_msg is mock_message
    queue_manager_instance.logger.info.assert_any_call(
        f"Found READY message ID {mock_message.id} in 'mentions' queue to play."
    )

# --- Test for get_active_queue_stats ---
@patch('tts_server.queue_manager.get_total_audio_size')
@patch('tts_server.queue_manager.get_messages_by_status')
def test_get_active_queue_stats(mock_get_messages_db, mock_get_total_audio_size_db,
                                queue_manager_instance, mock_db_session):
    """Test getting active queue statistics."""

    # Simulate return values for get_messages_by_status
    def get_messages_side_effect(db, status, queue_type, limit):
        if queue_type == "mentions":
            if status == MessageStatusEnum.PENDING: return [MagicMock()] * 3 # 3 pending
            if status == MessageStatusEnum.READY: return [MagicMock()] * 2   # 2 ready
            if status == MessageStatusEnum.ERROR: return [MagicMock()] * 1   # 1 error
            if status == MessageStatusEnum.PROCESSING: return [MagicMock()] * 0 # 0 processing
        return []
    mock_get_messages_db.side_effect = get_messages_side_effect
    
    # Simulate return value for get_total_audio_size for "mentions" queue
    mock_get_total_audio_size_db.return_value = 150 * 1024 * 1024 # 150MB

    stats = queue_manager_instance.get_active_queue_stats()

    assert stats["active_queue_type"] == "mentions"
    assert stats["pending_count"] == 3
    assert stats["ready_count"] == 2
    assert stats["error_count"] == 1
    assert stats["processing_count"] == 0
    assert stats["mentions_total_audio_size_bytes"] == 150 * 1024 * 1024
    
    # Check calls to get_messages_by_status for "mentions" queue
    # Order of these calls for different statuses doesn't strictly matter
    expected_calls_get_messages = [
        call(mock_db_session, status=MessageStatusEnum.PENDING, queue_type="mentions", limit=-1),
        call(mock_db_session, status=MessageStatusEnum.READY, queue_type="mentions", limit=-1),
        call(mock_db_session, status=MessageStatusEnum.ERROR, queue_type="mentions", limit=-1),
        call(mock_db_session, status=MessageStatusEnum.PROCESSING, queue_type="mentions", limit=-1)
    ]
    mock_get_messages_db.assert_has_calls(expected_calls_get_messages, any_order=True)
    
    # Check call to get_total_audio_size for "mentions" queue
    mock_get_total_audio_size_db.assert_called_once_with(mock_db_session, queue_type="mentions")


if __name__ == "__main__":
    pytest.main()
