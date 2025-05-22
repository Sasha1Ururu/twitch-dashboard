import soundfile as sf
import sounddevice as sd
from kokoro import KPipeline

pipeline = KPipeline(lang_code='a')
text = """And I will strike down upon thee with great vengeance and FURIOUS ANGER!!"""
voices = {
    1: {"name": "am_adam", "description": "Adam - Strong and confident"},
    # 2: {"name": "am_echo", "description": "Echo - Resonant and clear"},
    # 3: {"name": "am_eric", "description": "Eric - Professional and authoritative"},
    # 4: {"name": "am_fenrir", "description": "Fenrir - Deep and powerful"},
    # 5: {"name": "am_liam", "description": "Liam - Friendly and conversational"},
    6: {"name": "am_michael", "description": "Michael - Warm and trustworthy"},
    # 7: {"name": "am_onyx", "description": "Onyx - Rich and sophisticated"},
    # 8: {"name": "am_puck", "description": "Puck - Playful and energetic"},
}  # NOTE: #1 and #6 are the best
# Pre-load voice embeddings using minimal text
for voice_info in voices.values():
    list(pipeline(".", voice=voice_info['name'], speed=1.0))  # Single punctuation to load voice

# Load voice embeddings
voice_1 = pipeline.voices[voices[1]["name"]]  # Adam
voice_6 = pipeline.voices[voices[6]["name"]]  # Michael

# Mix voices
mix_ratio = 0.2
mixed_voice = (voice_1 * mix_ratio) + (voice_6 * (1 - mix_ratio))

# Register the mixed voice in the pipeline
pipeline.voices['mixed_voice'] = mixed_voice.squeeze(0)  # Ensure correct shape
print(pipeline.voices.keys())  # Check what voices exist

# Generate audio using the mixed voice
generator_mixed = pipeline(
    text, voice='mixed_voice',
    speed=0.75, split_pattern=r'\n+'
)

# Process and play the mixed voice output
for i, (gs, ps, audio) in enumerate(generator_mixed):
    print(f"Segment {i}: {gs}")
    print(f"Phonemes: {ps}")

    # Play the audio
    sd.play(audio, samplerate=24000)
    sd.wait()

    # Save the mixed voice output
    sf.write(f'audio/mixed_{i}.wav', audio, 24000)

print("Mixed voice generation complete!")