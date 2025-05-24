import pytest
import os
import tempfile
import shutil
import sys # Import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np # Import numpy

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from tts_server.main import app # The FastAPI app -> Moved into fixtures
from tts_server.config import settings # To override for tests
from tts_server.database import Base, get_db # For migrations and DB session
# from tts_server.tts_engine import TTSEngine # To mock its methods -> Moved into fixture

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig

# Store original settings values to restore them later
_original_settings_values = {}

@pytest.fixture(scope="session")
def test_db_session_factory():
    """
    Creates a temporary SQLite database and session factory for testing.
    Applies Alembic migrations to set up the schema.
    """
    global _original_settings_values
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file_path = Path(tmpdir) / "test_tts_database.db"
        test_db_url = f"sqlite:///{db_file_path}"

        # Store and override DATABASE_URL
        _original_settings_values['DATABASE_URL'] = settings.DATABASE_URL
        settings.DATABASE_URL = test_db_url
        
        # Run Alembic migrations
        # Ensure alembic.ini path is correct. If conftest.py is in tests/,
        # and alembic.ini is in tts_server/, this path needs to be relative to CWD
        # or absolute. Assuming CWD is project root when running pytest.
        alembic_cfg_path = "tts_server/alembic.ini" 
        
        # Verify alembic.ini exists at the expected path for clarity
        if not os.path.exists(alembic_cfg_path):
            # Fallback if tests are run from within tests/ directory, adjust path
            alt_alembic_cfg_path = "../tts_server/alembic.ini"
            if os.path.exists(alt_alembic_cfg_path):
                alembic_cfg_path = alt_alembic_cfg_path
            else:
                # If still not found, this will likely fail in AlembicConfig
                pytest.fail(f"Alembic config not found at {alembic_cfg_path} or {alt_alembic_cfg_path}. CWD: {os.getcwd()}")

        alembic_config = AlembicConfig(alembic_cfg_path)
        # No need to set script_location if it's correct in alembic.ini relative to its own path.
        # alembic.ini's script_location is %(here)s/alembic. If alembic.ini is in tts_server/,
        # and we are running from project root, then %(here)s is tts_server/.
        # The key is that sqlalchemy.url in env.py will use settings.DATABASE_URL.
        alembic_config.set_main_option("sqlalchemy.url", test_db_url) # Explicitly for safety

        # Before running migrations, ensure the env.py can find the tts_server package.
        # This might require adjusting sys.path if not running pytest from project root.
        # Assuming pytest is run from project root, `tts_server` is importable.
        try:
            alembic_upgrade(alembic_config, "head")
        except Exception as e:
            pytest.fail(f"Alembic upgrade failed: {e}. Ensure DB URL is correct and env.py can import tts_server modules. CWD: {os.getcwd()}")

        # Create engine and session for tests
        engine = create_engine(test_db_url, connect_args={"check_same_thread": False}) # check_same_thread for SQLite
        SessionLocal_test = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        yield SessionLocal_test # This is the factory

        # Teardown (though tempdir handles file cleanup)
        # Restore original settings
        settings.DATABASE_URL = _original_settings_values.get('DATABASE_URL')


@pytest.fixture(scope="session", autouse=True)
def override_get_db_for_tests(test_db_session_factory):
    """
    Overrides FastAPI's get_db dependency to use the test database session factory.
    Autouse=True and session scope ensure this applies to all tests.
    """
    from tts_server.main import app # Import app here
    def get_test_db():
        db = test_db_session_factory() # Get a new session
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides.clear() # Clean up overrides after tests


@pytest.fixture(scope="session")
def test_client(override_get_db_for_tests, mock_audio_output_dir): # Added mock_audio_output_dir
    from tts_server.main import app # Import app here
    """
    Provides a TestClient for making API requests to the FastAPI app.
    Ensures startup/lifespan events are run (for QueueManager setup, etc.).
    Uses the test database.
    """
    # override_get_db_for_tests ensures 'get_db' is patched to use test DB.
    # mock_audio_output_dir ensures settings.AUDIO_OUTPUT_DIRECTORY is set for tests.
    # mock_global_kokoro_module (autouse=True) ensures KPipeline is mocked.
    
    # Using TestClient as a context manager handles lifespan events (startup/shutdown).
    # This should ensure that app.on_event("startup") in main.py is executed,
    # which initializes QueueManager and sets up the api_module.get_queue_manager override.
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def mock_audio_output_dir():
    """
    Creates a temporary directory for audio output during tests.
    Overrides settings.AUDIO_OUTPUT_DIRECTORY.
    """
    global _original_settings_values
    with tempfile.TemporaryDirectory() as tmpdir:
        test_audio_dir = Path(tmpdir) / "test_audio_files"
        test_audio_dir.mkdir(exist_ok=True)

        _original_settings_values['AUDIO_OUTPUT_DIRECTORY'] = settings.AUDIO_OUTPUT_DIRECTORY
        settings.AUDIO_OUTPUT_DIRECTORY = str(test_audio_dir)
        
        yield str(test_audio_dir) # Provide the path to the test audio directory
        
        settings.AUDIO_OUTPUT_DIRECTORY = _original_settings_values.get('AUDIO_OUTPUT_DIRECTORY')


@pytest.fixture
def mock_tts_synthesize(mock_audio_output_dir): # Depends on temp audio dir fixture
    """
    Mocks TTSEngine.synthesize to return a dummy audio file path and size,
    and creates a small dummy file.
    Yields the mock object for further customization in tests.
    """
    from tts_server.tts_engine import TTSEngine # Import TTSEngine here
    with patch.object(TTSEngine, 'synthesize') as mock_synthesize:
        
        def default_side_effect(message_id, text_to_synthesize, output_directory):
            # Ensure output_directory from call matches mock_audio_output_dir from settings
            # This check is important if TTSEngine gets output_directory from settings vs argument.
            # TTSEngine.synthesize takes output_directory as an argument.
            # AudioProcessingWorker passes settings.AUDIO_OUTPUT_DIRECTORY to it.
            # So, output_directory in this function *should* be mock_audio_output_dir.
            
            if str(Path(output_directory)) != str(Path(mock_audio_output_dir)):
                 # This might indicate a problem in how settings are overridden or passed.
                 # For robust tests, one might raise an error here or log a warning.
                 # For now, proceed but it's a point of potential fragility.
                 pass


            filename = f"message_{message_id}_test.wav" # Use a distinct name for test files
            filepath = Path(output_directory) / filename
            
            # Create a small dummy file
            with open(filepath, 'w') as f:
                f.write("dummy audio content for test") # Content doesn't matter much
            
            file_size = os.path.getsize(filepath)
            return str(filepath), file_size

        mock_synthesize.side_effect = default_side_effect
        yield mock_synthesize # Test can now access mock_synthesize.return_value etc.


@pytest.fixture(scope="session", autouse=True)
def mock_global_kokoro_module(): # Renamed for clarity and simplified
    """
    Globally mocks the 'kokoro' module by inserting it into sys.modules.
    This mock contains a mock KPipeline class. This setup aims to prevent
    ModuleNotFoundError for 'kokoro' during test collection and execution.
    The mock KPipeline instance (returned by the mock KPipeline class) 
    has a 'voices' attribute initialized to {}, and its call simulates voice loading.
    """
    # Create a mock KPipeline class
    mock_kpipeline_class = MagicMock(name="MockKPipelineClass_Global")
    mock_pipeline_instance = MagicMock(name="MockKPipelineInstance_Global")
    mock_pipeline_instance.voices = dict() # Explicitly initialize as dict

    # Define the side effect for the pipeline instance call
    def mock_pipeline_call_effect(text, voice, speed, split_pattern=None):
        print(f"Mock KPipeline called with text: '{text}', voice: '{voice}', speed: {speed}") # Debugging
        # Simulate loading the voice embedding if not already present
        if voice not in mock_pipeline_instance.voices:
            # Use a simple, consistent dummy embedding for all voices loaded this way
            mock_pipeline_instance.voices[voice] = np.array([0.1, 0.2, 0.3], dtype=np.float32)
            print(f"Mock KPipeline: Added dummy embedding for '{voice}'. Current voices: {list(mock_pipeline_instance.voices.keys())}") # Debugging
        else:
            print(f"Mock KPipeline: Voice '{voice}' already has an embedding.") # Debugging
        
        # Simulate returning an audio segment generator
        yield np.array([0.01, 0.02, 0.03], dtype=np.float32) # Dummy audio segment

    mock_pipeline_instance.side_effect = mock_pipeline_call_effect
    # Ensure no direct .return_value is set on mock_pipeline_instance that would override side_effect
    # for the instance call itself. Setting it to None is safest if it might have been set.
    mock_pipeline_instance.return_value = None 

    mock_kpipeline_class.return_value = mock_pipeline_instance # KPipeline() returns mock_pipeline_instance

    # Create a mock 'kokoro' module
    mock_kokoro_module = MagicMock(name="MockKokoroModule_Global")
    mock_kokoro_module.KPipeline = mock_kpipeline_class

    original_kokoro = sys.modules.get('kokoro')
    sys.modules['kokoro'] = mock_kokoro_module
    
    yield # The primary effect is the sys.modules modification

    # Teardown: remove the mock 'kokoro' module or restore original
    if original_kokoro:
        sys.modules['kokoro'] = original_kokoro
    elif 'kokoro' in sys.modules and sys.modules['kokoro'] is mock_kokoro_module:
        # Ensure we only delete it if it's our mock and was not there originally
        del sys.modules['kokoro']
