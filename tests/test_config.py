import os
import json
import pytest
from unittest.mock import patch, mock_open
from pydantic_core import ValidationError # Added import

from tts_server.config import Settings

# Define a base path for where the tests might expect .env or files to be created
# This assumes tests might run from the project root.
TEST_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Project root

def test_default_settings_load():
    """Test that default settings are loaded correctly."""
    settings = Settings(_env_file=None) # Ensure no .env file is loaded for this test

    assert settings.DATABASE_URL == "sqlite:///./tts_server/tts_database.db"
    assert settings.AUDIO_OUTPUT_DIRECTORY == "tts_server/audio_files"
    assert settings.USERNAME == "YourTwitchUsername"
    assert settings.AUTOPLAY_COOLDOWN == 10
    assert settings.VOICE_CONFIG_STR == "adam50_michael50" # Corrected default
    assert settings.VOICE_MAPPINGS_JSON == '{"adam": "am_adam", "michael": "am_michael"}' # Corrected default
    assert settings.LANG_CODE == "en"
    assert settings.TTS_SERVER_HOST == "127.0.0.1"
    assert settings.TTS_SERVER_PORT == 8008
    assert settings.TTS_ENGINE_SPEED == 0.85
    assert settings.LOG_LEVEL == "INFO"
    assert settings.KOKORO_LANG_CODE == "a"
    assert settings.DEFAULT_VOICE == "adam" # Added assertion
    assert settings.WORKER_POLL_INTERVAL == 1.0

def test_voice_mappings_json_parsing():
    """Test that VOICE_MAPPINGS_JSON is correctly parsed."""
    valid_json_str = '{"friendly_name1": "kokoro_voice1", "friendly_name2": "kokoro_voice2"}'
    expected_dict = {"friendly_name1": "kokoro_voice1", "friendly_name2": "kokoro_voice2"}
    
    settings = Settings(VOICE_MAPPINGS_JSON=valid_json_str, _env_file=None)
    assert settings.parsed_voice_mappings == expected_dict

    # Test with invalid JSON
    invalid_json_str = '{"name": "voice1",, "name2": "voice2"}' # Extra comma
    with pytest.raises(ValueError) as excinfo:
        Settings(VOICE_MAPPINGS_JSON=invalid_json_str, _env_file=None)
    assert "Invalid JSON" in str(excinfo.value)

    # Test with non-dict JSON
    non_dict_json_str = '[1, 2, 3]'
    with pytest.raises(ValueError) as excinfo:
        Settings(VOICE_MAPPINGS_JSON=non_dict_json_str, _env_file=None)
    assert "must be a JSON object (dict)" in str(excinfo.value)

    # Test with non-string keys/values
    # JSON keys must be strings. json.loads() will fail before Pydantic validation.
    non_string_key_json_str = '{123: "voice1"}' # Invalid JSON: key is not a string
    # Pydantic V2 wraps json.JSONDecodeError in its own ValidationError
    with pytest.raises(ValidationError, match="Invalid JSON in VOICE_MAPPINGS_JSON"):
        Settings(VOICE_MAPPINGS_JSON=non_string_key_json_str, _env_file=None)

    # Example of a test that *would* check the string content type if JSON was valid:
    # valid_json_non_string_value_str = '{"key1": 123}' # Valid JSON, but value is not str
    # with pytest.raises(ValueError, match="All keys and values in VOICE_MAPPINGS_JSON must be strings"):
    #     Settings(VOICE_MAPPINGS_JSON=valid_json_non_string_value_str, _env_file=None)
    # This part is commented out as it's an example, the original test only had the invalid key case.

@patch("os.makedirs")
def test_audio_output_directory_creation(mock_makedirs):
    """Test that AUDIO_OUTPUT_DIRECTORY is created by Pydantic validator."""
    # The validator `ensure_audio_output_directory_exists` calls os.makedirs.
    # We patch os.makedirs to check if it's called.
    
    test_dir = "test_audio_output_dir_for_config_test"
    
    # Temporarily change the working directory for this test if paths are relative
    # However, Pydantic's path handling for .env and os.makedirs should generally work
    # based on the CWD when Settings() is instantiated.
    # For simplicity, we assume the default AUDIO_OUTPUT_DIRECTORY or a custom one.
    
    # Test with default directory
    Settings(_env_file=None) # Instantiating Settings should trigger the validator
    # The default dir is "tts_server/audio_files".
    # Check if makedirs was called with the default path.
    # Note: The path might be made absolute by os.makedirs or Pathlib internally.
    # For simplicity, we check if it was called with a path ending in the default.
    
    # Path used by validator: settings.AUDIO_OUTPUT_DIRECTORY (e.g. "tts_server/audio_files")
    default_dir_to_check = Settings.model_fields['AUDIO_OUTPUT_DIRECTORY'].default
    
    # Check if os.makedirs was called. The exact path check can be tricky due to CWD.
    # A more robust check might be to ensure it's called with the specific path.
    # For now, let's check it was called with the default dir.
    # We need to find the call that corresponds to the default directory.
    
    # Let's re-initialize to be sure about the call.
    mock_makedirs.reset_mock()
    Settings(AUDIO_OUTPUT_DIRECTORY=default_dir_to_check, _env_file=None)
    mock_makedirs.assert_any_call(default_dir_to_check, exist_ok=True)

    # Test with a custom directory
    mock_makedirs.reset_mock()
    Settings(AUDIO_OUTPUT_DIRECTORY=test_dir, _env_file=None)
    mock_makedirs.assert_called_with(test_dir, exist_ok=True)


def test_load_from_env_file():
    """Test loading settings from a .env file."""
    # Create a dummy .env file content
    dummy_env_content = (
        "DATABASE_URL=sqlite:///./dummy_test.db\n"
        "USERNAME=TestUserFromEnv\n"
        "AUTOPLAY_COOLDOWN=25\n"
        'VOICE_MAPPINGS_JSON={"env_key": "env_value"}\n'
    )
    expected_mappings = {"env_key": "env_value"}

    # Use mock_open to simulate the .env file
    # Pydantic's BaseSettings uses `find_dotenv` then `open`. We need to patch `open`
    # within the scope of where Pydantic settings load it, or provide a path.
    # The _env_file parameter is the easiest way to control this for testing.
    
    # Write dummy content to a temporary .env file for the test
    temp_env_file_path = os.path.join(TEST_BASE_DIR, "temp_test.env") # Place in project root for test
    
    try:
        with open(temp_env_file_path, "w") as f:
            f.write(dummy_env_content)

        settings = Settings(_env_file=temp_env_file_path) # Tell Pydantic to load this specific file

        assert settings.DATABASE_URL == "sqlite:///./dummy_test.db"
        assert settings.USERNAME == "TestUserFromEnv"
        assert settings.AUTOPLAY_COOLDOWN == 25
        assert settings.parsed_voice_mappings == expected_mappings
    
    finally:
        # Clean up the dummy .env file
        if os.path.exists(temp_env_file_path):
            os.remove(temp_env_file_path)

if __name__ == "__main__":
    pytest.main()
