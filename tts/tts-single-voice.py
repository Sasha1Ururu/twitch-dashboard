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
for voice_num in voices.keys():
    generator = pipeline(
        text, voice=voices[voice_num]['name'],  # <= change voice here
        speed=0.65,
        split_pattern=r'\n+'
    )
    for i, (gs, ps, audio) in enumerate(generator):
        print(i)  # i => index
        print(gs)  # gs => graphemes/text
        print(ps)  # ps => phonemes
        # Play audio using sounddevice
        sd.play(audio, samplerate=24000)
        sd.wait()  # Wait until audio playback finishes
        sf.write(f'audio/{voice_num}.wav', audio, 24000)  # save each audio file
