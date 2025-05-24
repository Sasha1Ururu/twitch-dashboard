## Intro
+ Server that receives text messages that needs to be TTSed.
+ Communication with the App can be via HTTP or WebSocket.
+ Utilizes a real database to store queues and played messages (meta data, no actual audio files).
+ Audio is stored in the filesystem (e.g., as WAV files, as suggested by the `kokoro` example). The whole current queue should be available as audio files as soon as possible.
+ TTS is performed using GPU power (consuming ~700..1000 MB, 3% of NVIDIA GeForce RTX 3060 12GB) via the selected TTS engine.
+ max queue length - do not exceed 200Mb of audio for mentions queue - how much is that? on overflow - delete oldest. for bits queue - no limit.
+ use Python, SQLite


### App UI
App UI has the following elements related to TTS:
1. 🗣️ 22 (queue size)
2. ▶ - [PLAY] button. Play a single item from the queue. Or start autoplay if [AUTOPLAY] toggle is active.
3. ⏹ - [STOP] button.
4. 📜 (or 🔁) - [AUTOPLAY] toggle.
5. 🗑️- Clear queue

### Config vars (Server-side)
+ `username`: Twitch username of the streamer (for parsing mentions).
+ `autoplay_cooldown`: Cooldown period in seconds between automatically played messages.
+ `voice`: A string defining the voice mix, e.g., "jared50_lex30_martha20".
    + This string indicates the base voices and their percentage in the final mix. For example, "jared50_lex30_martha20" would mean 50% of a voice mapped from "jared", 30% of a voice mapped from "lex", and 20% of a voice mapped from "martha".
    + A mapping will be required from these friendly names (e.g., "jared") to the specific voice model names used by the TTS engine (e.g., "am_adam" from the `kokoro` example).

### Queue Management and Message Handling

Two types of queues manage incoming messages:
1.  MentionsQueue:
    + Contains messages where the streamer's `username` (from server config) is mentioned (e.g., f"@{username}").
    + When the App is in a mode to send all chat messages, the server will parse these messages to filter and identify mentions to be added to this queue.
2.  BitsQueue:
    + Contains messages associated with Twitch Bits donations.
    + When the App is in "TTS - Only for Bits" mode, it will send only relevant `BitsMessage` objects to the server, which are then added to this queue.

Dataclasses for Messages (as defined by App):
```python
from dataclasses import dataclass

@dataclass
class Message:
    sent_by: str # username
    text: str    # message text

@dataclass
class BitsMessage(Message):
    bits_amount: int # bits sent with the message
```

### Behavior based on Active Queue Mode:
+ When in BitsQueue mode:
    + The App will primarily send `BitsMessage` objects.
    + The server will focus on processing and populating the `BitsQueue`.
    + For future consideration (not for initial implementation): The server could potentially have the capability to continue parsing all chat messages for mentions and updating the `MentionsQueue` in the background even when `BitsQueue` is the active playback queue. For the initial scope, if `BitsQueue` is active, the App does not send all chat messages for mention parsing.
+ When the App changes the "TTS - bits/mentions" setting, the server should:
    1. Persistently save current queue state: This means ensuring that any messages currently being processed or in an in-memory buffer related to the outgoing active queue are finalized in the database. The core message data itself should already be in the "real database."
    2. Load new queue: The server will switch its active context to the newly selected queue type (Mentions or Bits). Subsequent operations like "Play", "Queue Size", "Clear Queue" will target this new active queue.
+ Clearing the Queue:
    1. This action is only invoked by a "Clear queue" command from the App.
    2. Only the currently active queue (MentionsQueue or BitsQueue) should be affected.
    3. Messages in the active queue that are pending or ready for playback are softly deleted:
        + Associated audio files are deleted from the filesystem.
        + Their corresponding DB entries are marked as "is_deleted" (or a similar status), and a timestamp of this action (e.g., `timestamp_deleted`) should be updated/recorded.
    4. Played messages or messages with errors in the active queue are typically not affected by a standard clear operation, unless specified otherwise.

### TTS engine (`kokoro` based)

The TTS engine will utilize the `kokoro` library as demonstrated in the provided example.

Initialization (Server Startup):
1. Initialize the `KPipeline`:
```python
    from kokoro import KPipeline
    pipeline = KPipeline(lang_code='en') # Assuming 'en' or configurable lang_code
```
2. Parse the `voice` config string (e.g., "jared50_lex30_martha20").
    + Extract base voice identifiers (e.g., "jared", "lex", "martha") and their percentages.
    + Map these identifiers to specific `kokoro` voice model names (e.g., "jared" -> "am_adam", "martha" -> "am_michael"). This mapping needs to be defined (e.g., in server configuration). For example, based on the Python snippet, "am_adam" and "am_michael" were good voices.
3. Pre-load the required base `kokoro` voice models:
```python
    # Example using voices from the snippet
    # This would be dynamic based on parsed voice config
    base_voices_to_load = {
        "am_adam": {"name": "am_adam"}, # Mapped from "jared"
        "am_michael": {"name": "am_michael"} # Mapped from "martha"
        # ... other voices based on config
    }
    for voice_info in base_voices_to_load.values():
        list(pipeline(".", voice=voice_info['name'], speed=1.0)) # Minimal text to load
```
4. Load the voice embeddings for the configured base voices:
```python
    # Example for a two-voice mix based on "jared50_martha50" (simplified from original example)
    voice_1_emb = pipeline.voices["am_adam"] # Assuming "jared" maps to "am_adam"
    voice_2_emb = pipeline.voices["am_michael"] # Assuming "martha" maps to "am_michael"
```
5. Create the mixed voice embedding based on the configured percentages:
```python
    # Example for jared50_martha50
    # mix_ratio_1 = 0.50 # for voice_1 (jared/am_adam)
    # mix_ratio_2 = 0.50 # for voice_2 (martha/am_michael)
    # mixed_voice_emb = (voice_1_emb * mix_ratio_1) + (voice_2_emb * mix_ratio_2)
    # This needs to be generalized for N voices from the config string.
    # For the example "jared50_lex30_martha20":
    # mixed_voice_emb = (voice_jared_emb * 0.50) + (voice_lex_emb * 0.30) + (voice_martha_emb * 0.20)
```
6. Register the final mixed voice in the pipeline:
```python
    pipeline.voices['custom_mixed_voice'] = mixed_voice_emb.squeeze(0) # Ensure correct shape
```
Audio Generation (for each message):
1. Retrieve the `text` for the message to be synthesized.
2. Use the initialized `pipeline` with the `custom_mixed_voice`:
```python
    import soundfile as sf
    import numpy as np # For concatenating audio if needed
    import os

    # text = "The message text to synthesize"
    # configured_speed = 0.75 # Or from config/message properties
    # audio_output_directory = "audio/" # From server config

    generator = pipeline(
        text,
        voice='custom_mixed_voice',
        speed=configured_speed,
        split_pattern=r'\n+' # Or other suitable pattern
    )

    audio_segments = []
    for i, (gs, ps, audio_segment) in enumerate(generator):
        # gs: grapheme segment, ps: phoneme segment
        audio_segments.append(audio_segment)

    if audio_segments:
        final_audio = np.concatenate(audio_segments) if len(audio_segments) > 1 else audio_segments[0]
        
        # Determine a unique filename, e.g., based on message ID
        output_filename = f"message_{message_id}.wav" # Placeholder for actual naming convention
        output_path = os.path.join(audio_output_directory, output_filename)
        
        sf.write(output_path, final_audio, samplerate=24000) # kokoro default samplerate
        # Store output_path in the database for the message
    else:
        # Handle cases where no audio is generated (e.g., empty text)
        print(f"Warning: No audio generated for text: {text}")
```
3. The generated audio file (e.g., `message_xyz.wav`) is saved to the filesystem (`audio_output_directory`), and its path is stored in the database associated with the message.
