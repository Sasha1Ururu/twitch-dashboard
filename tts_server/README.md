# TTS Server Overview

This is a Python-based Text-to-Speech (TTS) server using FastAPI. It's designed to manage TTS requests, queue them, generate audio using a TTS engine (assumed to be `kokoro-tts`), and provide API endpoints for interaction and control.

**Key Features**:
*   **Dual Queue System**: Separate queues for "mentions" and "bits" (or other types) of messages.
*   **Database Backend**: Uses SQLite by default, with SQLAlchemy and Alembic for schema management and migrations.
*   **Configurable Voice Mixing**: Allows defining mixed voices by specifying ratios of different base voices.
*   **Background Audio Generation**: A dedicated worker thread processes messages and generates audio files.
*   **Static Audio File Serving**: Generated audio files are served statically.
*   **Autoplay Functionality**: Can automatically trigger playback of messages from the active queue.
*   **API Control**: Endpoints to add messages, manage queues, control autoplay, and view configuration.

## Project Structure

*   `main.py`: Main FastAPI application; initializes services, workers, and runs the server.
*   `api.py`: FastAPI routers and API endpoint definitions.
*   `config.py`: Pydantic-based configuration management (loads settings from `.env` and environment variables).
*   `database.py`: SQLAlchemy models (e.g., `TTSMessage`), database session management, and CRUD operations.
*   `tts_engine.py`: Wraps the TTS engine (`kokoro-tts`) for voice loading, mixing, and audio synthesis.
*   `queue_manager.py`: Manages message queues (e.g., "mentions", "bits") stored in the database.
*   `audio_worker.py`: Background thread responsible for processing messages from the queue and generating audio files.
*   `alembic/`: Directory containing Alembic database migration scripts.
*   `audio_files/`: Default directory for storing generated `.wav` audio files. (Configurable via `AUDIO_OUTPUT_DIRECTORY`)
*   `.env`: File for environment-specific configurations (not version-controlled).
*   `.env.example`: Example configuration file.

## Setup and Installation

1.  **Python Version**: Python 3.9+ is recommended.
2.  **Clone Repository**:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
3.  **Create Virtual Environment**:
    ```bash
    python -m venv venv
    ```
    Activate it:
    *   Linux/macOS: `source venv/bin/activate`
    *   Windows: `venv\Scripts\activate`
4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    **Note on `kokoro-tts`**: This project assumes `kokoro-tts` is available and installable in your target environment. It is not currently available on PyPI. You may need to install it from a local source or a private repository if you have access to it.

## Configuration

Server settings are managed via environment variables, which can be placed in a `.env` file inside the `tts_server/` directory.
Copy `tts_server/.env.example` to `tts_server/.env` and customize it:

```bash
cp tts_server/.env.example tts_server/.env
```

Edit `tts_server/.env` with your desired settings. Key variables include:

*   `DATABASE_URL`: SQLAlchemy database connection string (default: `sqlite:///./tts_server/tts_database.db`).
*   `AUDIO_OUTPUT_DIRECTORY`: Path to store generated audio files (default: `tts_server/audio_files`).
*   `USERNAME`: Twitch username (used for context, e.g., if app integrates with Twitch).
*   `AUTOPLAY_COOLDOWN`: Cooldown period (seconds) between autoplayed messages (default: `10`).
*   `VOICE_CONFIG_STR`: Defines the voice mix, e.g., `"jared50_lex30_martha20"` (default: `"am_adam50_am_michael50"`).
*   `VOICE_MAPPINGS_JSON`: JSON string mapping friendly names to internal Kokoro voice names, e.g., `'{"jared": "am_jared_voice", "lex": "am_lex_voice"}'`.
*   `KOKORO_LANG_CODE`: Language code for the Kokoro TTS engine (default: `"a"`).
*   `TTS_ENGINE_SPEED`: Speech speed for the TTS engine (default: `0.85`).
*   `TTS_SERVER_HOST`: Host address for the server (default: `"127.0.0.1"`).
*   `TTS_SERVER_PORT`: Port for the server (default: `8008`).
*   `LOG_LEVEL`: Logging level (e.g., `INFO`, `DEBUG`) (default: `"INFO"`).
*   `WORKER_POLL_INTERVAL`: Interval (seconds) for the audio worker to poll for new messages (default: `1.0`).

## Database Migrations

Database schema changes are managed using Alembic.

*   **Apply Migrations**: To apply existing migrations and bring the database to the latest version:
    ```bash
    alembic -c tts_server/alembic.ini upgrade head
    ```
    This command should be run from the project root directory. The `alembic.ini` file is located in `tts_server/`.

*   **Create New Migrations**: If you change SQLAlchemy models in `database.py`:
    1.  Generate a new revision script:
        ```bash
        alembic -c tts_server/alembic.ini revision -m "your_description_of_change"
        ```
    2.  Alembic will create a new file in `tts_server/alembic/versions/`. Edit this file to include the specific `op.create_table()`, `op.add_column()`, etc., operations in the `upgrade()` function, and corresponding drop operations in `downgrade()`.

## Running the Server

The server is run using Uvicorn, an ASGI server.

1.  Ensure your virtual environment is activated and dependencies are installed.
2.  Make sure your `tts_server/.env` file is configured.
3.  Run the Uvicorn command from the project root directory:
    ```bash
    uvicorn tts_server.main:app --host <your_host> --port <your_port> --reload
    ```
    *   Replace `<your_host>` with the host address (e.g., `0.0.0.0` to listen on all interfaces, or `127.0.0.1` for local only).
    *   Replace `<your_port>` with the desired port number.
    *   The `--reload` flag enables auto-reloading on code changes, useful for development. Remove it for production.

    Example using default settings:
    ```bash
    uvicorn tts_server.main:app --host 0.0.0.0 --port 8008 --reload
    ```

4.  The server will be accessible at `http://<your_host>:<your_port>`.
5.  API documentation (Swagger UI) will be available at `http://<your_host>:<your_port>/docs`.

## API Endpoints Summary

All endpoints are prefixed with `/api/tts`.

*   `POST /add_message`: Adds a new message to the TTS queue.
    *   Payload includes `sent_by`, `text`, `bits_amount` (optional), and `message_type` ("mention" or "bits").
*   `GET /active_queue_stats`: Retrieves statistics for the currently active queue (e.g., pending/ready counts, total audio size for mentions queue, autoplay status).
*   `POST /play_next`: Gets the next message from the active queue that is ready to be played. Marks it as `PLAYING`.
    *   Returns message details and the path to the audio file.
*   `POST /mark_played/{message_id}`: Marks a specific message (by ID) as `PLAYED`.
*   `POST /autoplay/start`: Enables the autoplay feature.
*   `POST /autoplay/stop`: Disables the autoplay feature.
*   `POST /clear_active_queue`: Clears all `PENDING` and `READY` messages from the currently active queue by marking them as `DELETED`.
*   `POST /switch_active_queue`: Switches the active queue between "mentions" and "bits".
    *   Payload includes `queue_type` ("mentions" or "bits").
*   `GET /config`: Retrieves a subset of the current server configuration (e.g., voice settings, cooldowns).

Generated audio files are served from the `/audio/` path. For example, if a message `123` generates `message_123.wav`, it might be accessible at `http://<host>:<port>/audio/message_123.wav`.
