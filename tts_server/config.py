import os
import json
from typing import Dict, Any, Optional
from pydantic import BaseSettings, validator, root_validator

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./tts_server/tts_database.db"
    AUDIO_OUTPUT_DIRECTORY: str = "tts_server/audio_files"
    USERNAME: str = "YourTwitchUsername"
    AUTOPLAY_COOLDOWN: int = 10  # seconds
    VOICE_CONFIG_STR: str = "am_adam50_am_michael50"
    VOICE_MAPPINGS_JSON: str = '{"am_adam": "am_adam", "am_michael": "am_michael"}'
    LANG_CODE: str = "en"
    TTS_SERVER_HOST: str = "127.0.0.1"
    TTS_SERVER_PORT: int = 8008
    TTS_ENGINE_SPEED: float = 0.85
    LOG_LEVEL: str = "INFO"
    KOKORO_LANG_CODE: str = "a" # as used in tts/tts.py
    WORKER_POLL_INTERVAL: float = 1.0 # seconds

    # This field will be populated by the validator, not loaded from .env
    parsed_voice_mappings: Optional[Dict[str, str]] = None

    @validator("VOICE_MAPPINGS_JSON", always=True)
    def parse_voice_mappings_json(cls, v: str, values: Dict[str, Any]) -> str:
        try:
            parsed_map = json.loads(v)
            if not isinstance(parsed_map, dict):
                raise ValueError("VOICE_MAPPINGS_JSON must be a JSON object (dict).")
            for key, value in parsed_map.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError("All keys and values in VOICE_MAPPINGS_JSON must be strings.")
            values["parsed_voice_mappings"] = parsed_map
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in VOICE_MAPPINGS_JSON: {e}")
        return v # Return the original string value for VOICE_MAPPINGS_JSON field

    # Using root_validator to ensure AUDIO_OUTPUT_DIRECTORY is available
    @root_validator(skip_on_failure=True) # pre=False (default for root_validator)
    def ensure_audio_output_directory_exists(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        audio_dir = values.get("AUDIO_OUTPUT_DIRECTORY")
        if audio_dir:
            try:
                # Construct path relative to project root if needed, or ensure it's absolute
                # For now, assume AUDIO_OUTPUT_DIRECTORY is relative to where the app runs
                # or an absolute path.
                # If `tts_server` is the root for execution, then `tts_server/audio_files` works.
                # If `/app` is the root, then `tts_server/audio_files` also implies `/app/tts_server/audio_files`.
                
                # Let's ensure the path is relative to the project root (where .env might be)
                # or handle absolute paths correctly.
                # If AUDIO_OUTPUT_DIRECTORY is like "tts_server/audio_files", it's relative.
                # If it's "/abs/path/audio_files", it's absolute.
                
                # Assuming the .env file is at the project root, and paths are relative to it.
                # Pydantic loads .env from current working directory or specified path.
                # If config.py is in tts_server/, and script is run from project root,
                # paths like "tts_server/audio_files" are correct.
                
                os.makedirs(audio_dir, exist_ok=True)
            except OSError as e:
                # Handle error (e.g., log it or raise a more specific exception)
                # For now, raising ValueError to indicate a configuration problem.
                raise ValueError(f"Could not create audio output directory '{audio_dir}': {e}")
        else:
            # This case should ideally not happen if AUDIO_OUTPUT_DIRECTORY has a default.
            raise ValueError("AUDIO_OUTPUT_DIRECTORY is not set.")
            
        return values

    class Config:
        # Pydantic will look for a .env file in the current directory
        # (or an ancestor directory if find_dotenv is used with python-dotenv)
        # and load variables from it.
        env_file = ".env" # Specifies the default .env file name
        env_file_encoding = "utf-8"
        # extra = "ignore" # If you want to ignore extra fields in .env

# Create the settings instance. This will load from .env or use defaults.
settings = Settings()

# Example of how to access the parsed mappings:
# print(settings.parsed_voice_mappings)
# Example of how to access other settings:
# print(settings.DATABASE_URL)

# The old way of creating the directory is now handled by the validator.
# if not os.path.exists(settings.AUDIO_OUTPUT_DIRECTORY):
#     os.makedirs(settings.AUDIO_OUTPUT_DIRECTORY)

# Remove old variables if they were defined globally in this file
# (e.g., DATABASE_URL = os.getenv(...))
# The settings instance is now the single source of truth for config values.
