import os
import soundfile as sf
import numpy as np
import logging
from kokoro import KPipeline # Assuming this will work in the final environment

# Default logger if none is provided to the class
default_logger = logging.getLogger(__name__)
# Basic configuration for the default logger (can be customized by the application)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


from typing import Optional, List, Tuple, Dict # Added for type hints

class TTSEngine:
    def __init__(self, lang_code: str, voice_config_str: str,
                 voice_mappings: dict, tts_speed: float,
                 default_voice_friendly_name: Optional[str] = None, # New parameter
                 logger=None):
        """
        Initializes the TTS Engine.
        Args:
            lang_code (str): Language code for KPipeline.
            voice_config_str (str): Voice configuration string (e.g., "jared50_lex30_martha20").
            voice_mappings (dict): Mappings from friendly names to kokoro internal voice names.
            tts_speed (float): Speed for TTS synthesis.
            default_voice_friendly_name (Optional[str]): Default friendly voice name to use if ratios sum < 1.0 or are 0.
            logger: A Python logger instance. Uses a default logger if None.
        """
        self.logger = logger if logger else default_logger
        # Add detailed input logging here
        self.logger.info(f"TTSEngine __init__ received: lang_code='{lang_code}', voice_config_str='{voice_config_str}', voice_mappings_keys={list(voice_mappings.keys()) if voice_mappings else None}, tts_speed={tts_speed}, default_voice_friendly_name='{default_voice_friendly_name}'")
        self.logger.info(f"Initializing TTSEngine with lang_code='{lang_code}', speed={tts_speed}") # Original info log
        self.logger.debug(f"Voice config string: '{voice_config_str}', Mappings: {voice_mappings}, Default friendly voice: {default_voice_friendly_name}")

        try:
            self.pipeline = KPipeline(lang_code=lang_code)
            self.tts_speed = tts_speed
            self.default_voice_friendly_name = default_voice_friendly_name # Store new parameter
            
            parsed_voice_data = self._parse_voice_config(
                voice_config_str, 
                voice_mappings,
                self.default_voice_friendly_name # Pass to parser
            )
            self.logger.info(f"Parsed voice data: {parsed_voice_data}")
            
            self._load_and_mix_voices(parsed_voice_data)
            self.logger.info("TTSEngine initialized successfully with custom mixed voice.")
            
        except ValueError as ve:
            self.logger.error(f"ValueError during TTSEngine initialization: {ve}")
            raise  # Re-raise critical errors
        except Exception as e:
            self.logger.error(f"Unexpected error during TTSEngine initialization: {e}", exc_info=True)
            # Depending on policy, might re-raise or handle to allow app to start degraded
            raise RuntimeError(f"Failed to initialize TTSEngine: {e}")

    def _parse_voice_config(self, voice_config_str: str, voice_mappings: Dict[str, str], 
                            default_voice_friendly_name: Optional[str]) -> List[Tuple[str, float]]:
        """
        Parses the voice configuration string and applies new logic for default voice and normalization.
        """
        # Add detailed input logging here
        self.logger.info(f"TTSEngine _parse_voice_config received: voice_config_str='{voice_config_str}', voice_mappings_keys={list(voice_mappings.keys()) if voice_mappings else None}, default_voice_friendly_name='{default_voice_friendly_name}'")
        self.logger.debug(
            f"Parsing voice config: '{voice_config_str}' with mappings: {voice_mappings}, "
            f"default_voice: '{default_voice_friendly_name}'"
        )

        if not voice_config_str:
            self.logger.error("Voice configuration string is empty.")
            # This case should be handled by the new logic: if config is empty, sum_ratios will be 0,
            # and default voice should be used. If default voice is also not set, then it's an error.
            # Let's keep the explicit check for clarity, but adapt the logic.
            # If voice_config_str is empty, initial_parsed_voices will be empty, sum_ratios = 0.
            # The logic for sum_ratios == 0 will then apply.
            pass # Allow to proceed to sum_ratios logic

        initial_parsed_voices: List[Tuple[str, float]] = []
        
        if voice_config_str: # Only parse if not empty
            parts = voice_config_str.split('_')
            for part in parts:
                try:
                    name_part = ""
                    percent_part_str = ""
                    for char_idx in range(len(part) - 1, -1, -1):
                        if part[char_idx].isdigit():
                            percent_part_str = part[char_idx] + percent_part_str
                        else:
                            name_part = part[:char_idx + 1]
                            break
                    
                    if not name_part or not percent_part_str:
                        self.logger.error(f"Could not separate name and percentage from part '{part}'.")
                        raise ValueError(f"Could not separate name and percentage from part '{part}'.")

                    friendly_name = name_part
                    percentage = int(percent_part_str)

                    if friendly_name not in voice_mappings:
                        self.logger.error(f"Friendly name '{friendly_name}' not found in voice_mappings.")
                        raise ValueError(f"Voice name '{friendly_name}' not found in mappings.")
                    
                    kokoro_voice_name = voice_mappings[friendly_name]
                    initial_parsed_voices.append((kokoro_voice_name, float(percentage) / 100.0))
                
                except ValueError as e:
                    self.logger.error(f"Error parsing voice part '{part}': {e}")
                    raise ValueError(f"Invalid format in voice part '{part}': {e}")
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing voice part '{part}': {e}")
                    raise ValueError(f"Unexpected error parsing voice part '{part}'.")

        current_sum_ratios = sum(ratio for _, ratio in initial_parsed_voices)
        self.logger.debug(f"Initial parsed voices: {initial_parsed_voices}, sum of ratios: {current_sum_ratios:.4f}")

        final_voices: List[Tuple[str, float]] = []
        epsilon = 1e-9

        if not voice_config_str and not default_voice_friendly_name:
             self.logger.error("Voice configuration string is empty and no default voice is specified.")
             raise ValueError("Voice configuration string cannot be empty if no default voice is specified.")

        if abs(current_sum_ratios) < epsilon: # Handles empty voice_config_str or all ratios are zero (e.g. "adam0")
            self.logger.info(f"Sum of ratios is {current_sum_ratios:.4f}. Using default voice.")
            if not default_voice_friendly_name:
                self.logger.error("Default voice friendly name not provided, but required when ratios sum to 0.")
                raise ValueError("Default voice must be specified when voice_config_str sums to 0% or is empty.")
            if default_voice_friendly_name not in voice_mappings:
                self.logger.error(f"Default voice '{default_voice_friendly_name}' not found in voice mappings.")
                raise ValueError(f"Default voice '{default_voice_friendly_name}' not found in voice mappings.")
            
            default_kokoro_name = voice_mappings[default_voice_friendly_name]
            final_voices = [(default_kokoro_name, 1.0)]
            self.logger.info(f"Using default voice: {final_voices}")

        elif current_sum_ratios > epsilon and current_sum_ratios < 1.0 - epsilon: # Sum is > 0 and < 1
            self.logger.info(f"Sum of ratios ({current_sum_ratios:.4f}) is less than 1.0. Adding default voice for remainder.")
            if not default_voice_friendly_name:
                self.logger.error("Default voice friendly name not provided, but required when ratios sum to less than 1.0.")
                raise ValueError("Default voice must be specified when voice_config_str sums to less than 100%.")
            if default_voice_friendly_name not in voice_mappings:
                self.logger.error(f"Default voice '{default_voice_friendly_name}' not found in voice mappings.")
                raise ValueError(f"Default voice '{default_voice_friendly_name}' not found in voice mappings.")

            default_kokoro_name = voice_mappings[default_voice_friendly_name]
            remainder_ratio = 1.0 - current_sum_ratios
            
            final_voices_dict: Dict[str, float] = {name: ratio for name, ratio in initial_parsed_voices}
            final_voices_dict[default_kokoro_name] = final_voices_dict.get(default_kokoro_name, 0.0) + remainder_ratio
            final_voices = list(final_voices_dict.items())
            self.logger.info(f"Added/updated default voice. Final mix: {final_voices}")

        elif current_sum_ratios > 1.0 + epsilon: # Sum is > 1
            self.logger.warning(
                f"Total ratio from voice config ({current_sum_ratios:.4f}) is > 1.0. Normalizing explicitly parsed voices."
            )
            # Normalize only the explicitly parsed voices
            normalized_voices = []
            for name, ratio in initial_parsed_voices:
                normalized_voices.append((name, ratio / current_sum_ratios))
            final_voices = normalized_voices
            self.logger.info(f"Normalized voice ratios: {final_voices}")
        
        else: # Sum is approximately 1.0 (or initial_parsed_voices was empty but default logic handled it)
            if not initial_parsed_voices and final_voices: # Default voice was used due to empty config
                pass # final_voices already set
            elif initial_parsed_voices: # Original sum was ~1.0 or config was empty but default voice not used (error)
                final_voices = initial_parsed_voices
                self.logger.info(f"Using provided voice config as is (sum is approx 1.0): {final_voices}")
            # If initial_parsed_voices is empty and final_voices is also empty (e.g. empty config, no default),
            # an error should have been raised earlier.

        # Final check for sum of ratios (should be very close to 1.0 after normalization or default addition)
        final_sum_ratios = sum(r for _, r in final_voices)
        if not abs(final_sum_ratios - 1.0) < 1e-7:
            self.logger.error(f"Sum of final voice ratios ({final_sum_ratios}) is not 1.0. This is unexpected. Voices: {final_voices}")
            raise ValueError(f"Voice percentages do not sum to 1.0 even after processing (sum: {final_sum_ratios}).")

        if not final_voices: # Should be caught by earlier checks, but as a safeguard
            self.logger.error("Resulting voice configuration is empty, which is invalid.")
            raise ValueError("Could not determine a valid voice configuration.")
            
        return final_voices

    def _load_and_mix_voices(self, parsed_voice_data: List[Tuple[str, float]]):
        """
        Loads individual voices, retrieves embeddings, mixes them, and registers the custom voice.
        """
        self.logger.info("Loading and mixing voices...")
        self.logger.debug(f"Parsed voice data for mixing: {parsed_voice_data}")

        unique_kokoro_voice_names = sorted(list(set(name for name, _ in parsed_voice_data)))
        
        self.logger.info(f"Unique Kokoro voice names to load: {unique_kokoro_voice_names}")

        for voice_name in unique_kokoro_voice_names:
            if voice_name not in self.pipeline.voices:
                self.logger.info(f"Pre-loading voice model for '{voice_name}'...")
                try:
                    # Use minimal text to load the voice embedding
                    self.logger.debug(f"Before pre-load call for '{voice_name}'. Current pipeline.voices keys: {list(self.pipeline.voices.keys())}")
                    _ = list(self.pipeline(".", voice=voice_name, speed=1.0)) 
                    self.logger.debug(f"After pre-load call for '{voice_name}'. Current pipeline.voices keys: {list(self.pipeline.voices.keys())}")
                    self.logger.info(f"Successfully pre-loaded voice '{voice_name}'.")
                except Exception as e:
                    self.logger.error(f"Failed to pre-load voice '{voice_name}': {e}", exc_info=True)
                    raise ValueError(f"Could not load required voice embedding for '{voice_name}'.")
            else:
                self.logger.info(f"Voice '{voice_name}' already loaded or available in pipeline.")

        mixed_voice_emb = None
        first_voice = True

        for kokoro_voice_name, ratio in parsed_voice_data:
            if ratio == 0: # Skip voices with 0 contribution
                self.logger.info(f"Skipping voice '{kokoro_voice_name}' due to 0% ratio.")
                continue

            if kokoro_voice_name not in self.pipeline.voices:
                self.logger.error(f"Voice embedding for '{kokoro_voice_name}' not found in pipeline after load attempt.")
                raise ValueError(f"Voice embedding for '{kokoro_voice_name}' is missing.")
            
            voice_emb = self.pipeline.voices[kokoro_voice_name]
            self.logger.debug(f"Retrieved embedding for '{kokoro_voice_name}'. Shape: {voice_emb.shape if hasattr(voice_emb, 'shape') else 'N/A'}")

            if first_voice:
                mixed_voice_emb = voice_emb * ratio
                first_voice = False
            else:
                if mixed_voice_emb is None: # Should not happen if parsed_voice_data is not empty and ratios > 0
                     self.logger.error("mixed_voice_emb is None unexpectedly during mixing.")
                     raise ValueError("Error initializing mixed voice embedding.")
                mixed_voice_emb += (voice_emb * ratio)
            
            self.logger.info(f"Mixed voice '{kokoro_voice_name}' with ratio {ratio*100:.2f}%.")

        if mixed_voice_emb is None:
            self.logger.error("No voices were mixed. This could be due to all ratios being zero or empty parsed_voice_data.")
            raise ValueError("Cannot create custom mixed voice: no voice data to mix.")

        # Ensure correct shape (squeeze(0) was used in tts/tts.py example)
        # The exact shape requirement might depend on KPipeline's internals.
        # If KPipeline expects [1, D] and voice_emb is [1, D], then mixed_voice_emb will be [1,D]
        # If KPipeline.voices stores embeddings as [D] (squeezed), then we might need to ensure that.
        # Based on `self.pipeline.voices['custom_mixed_voice'] = mixed_voice_emb.squeeze(0)` from tts.py
        # it implies the stored embeddings should be 1D [D].
        # However, if individual `self.pipeline.voices[kokoro_voice_name]` are already [D],
        # then `mixed_voice_emb` would also be [D], and squeeze(0) might be unnecessary or error if it's already 1D.
        # Let's assume `pipeline.voices` stores [1, D] and we need to store [D] for 'custom_mixed_voice'.
        
        # Check shape before squeeze
        self.logger.debug(f"Shape of raw mixed_voice_emb: {mixed_voice_emb.shape if hasattr(mixed_voice_emb, 'shape') else 'N/A'}")
        if hasattr(mixed_voice_emb, 'squeeze') and mixed_voice_emb.ndim > 1: # Only squeeze if more than 1D
             final_mixed_emb = mixed_voice_emb.squeeze(0)
        else:
             final_mixed_emb = mixed_voice_emb

        self.pipeline.voices['custom_mixed_voice'] = final_mixed_emb
        self.logger.info(f"Registered 'custom_mixed_voice'. Final embedding shape: {final_mixed_emb.shape if hasattr(final_mixed_emb, 'shape') else 'N/A'}")


    def synthesize(self, message_id: any, text_to_synthesize: str, output_directory: str) -> tuple:
        """
        Synthesizes audio from text using the custom mixed voice and saves it.
        Args:
            message_id (any): Unique identifier for the message (used in filename).
            text_to_synthesize (str): The text to convert to speech.
            output_directory (str): Directory to save the audio file.

        Returns:
            tuple: (output_path, audio_file_size_bytes) or (None, 0) if failed.
        """
        self.logger.info(f"Synthesizing audio for message ID '{message_id}': '{text_to_synthesize[:50]}...'")
        
        if not os.path.exists(output_directory):
            try:
                os.makedirs(output_directory, exist_ok=True)
                self.logger.info(f"Created output directory: {output_directory}")
            except OSError as e:
                self.logger.error(f"Could not create output directory {output_directory}: {e}")
                return None, 0
        
        output_filename = f"message_{message_id}.wav"
        output_path = os.path.join(output_directory, output_filename)

        try:
            audio_segments = []
            # Using split_pattern=r'\n+' as specified
            # KPipeline returns a generator of audio segments (numpy arrays)
            for audio_segment in self.pipeline(
                text_to_synthesize, 
                voice='custom_mixed_voice', 
                speed=self.tts_speed,
                split_pattern=r'\n+' # Default is r'[.?!]+\s*', so \n+ handles line breaks
            ):
                audio_segments.append(audio_segment)

            if not audio_segments:
                self.logger.warning(f"No audio segments produced for message ID '{message_id}'. Text: '{text_to_synthesize}'")
                return None, 0

            # Concatenate segments if multiple, else take the first
            if len(audio_segments) > 1:
                final_audio = np.concatenate(audio_segments)
            else:
                final_audio = audio_segments[0]
            
            self.logger.debug(f"Final audio data shape: {final_audio.shape if hasattr(final_audio, 'shape') else 'N/A'}, dtype: {final_audio.dtype if hasattr(final_audio, 'dtype') else 'N/A'}")

            # Save the audio file (assuming 24000 Hz from kokoro examples)
            samplerate = 24000 # Standard for kokoro
            sf.write(output_path, final_audio, samplerate=samplerate)
            
            audio_file_size_bytes = os.path.getsize(output_path)
            self.logger.info(f"Audio for message ID '{message_id}' saved to '{output_path}', size: {audio_file_size_bytes} bytes.")
            
            return output_path, audio_file_size_bytes

        except FileNotFoundError: # sf.write can raise this if path is bad, though makedirs should prevent.
            self.logger.error(f"FileNotFoundError during synthesis for message ID '{message_id}'. Path: {output_path}", exc_info=True)
            return None, 0
        except Exception as e:
            self.logger.error(f"Error during TTS synthesis for message ID '{message_id}': {e}", exc_info=True)
            # Clean up partially created file if it exists and an error occurred
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                    self.logger.info(f"Cleaned up partial file: {output_path}")
                except OSError as rm_err:
                    self.logger.error(f"Could not remove partial file {output_path}: {rm_err}")
            return None, 0

# Example usage (for testing purposes, not part of the final class normally)
if __name__ == "__main__":
    # Configure a basic logger for the example
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main_logger = logging.getLogger("TTSEngineExample")

    # This example will not run without a functional KPipeline and voice models.
    # It's here for illustrative purposes of how the class might be called.
    main_logger.info("Starting TTSEngine example (requires functional KPipeline).")
    
    # Dummy KPipeline for structure testing if kokoro is not available
    class DummyKPipeline:
        def __init__(self, lang_code):
            self.lang_code = lang_code
            self.voices = {} # Stores voice embeddings
            main_logger.info(f"DummyKPipeline initialized with lang_code: {lang_code}")

        def __call__(self, text, voice, speed, split_pattern):
            main_logger.info(f"DummyKPipeline called with text: '{text[:20]}...', voice: {voice}, speed: {speed}")
            # Simulate yielding audio segments
            # Each segment is a numpy array of float32 samples
            sample_rate = 24000
            duration_per_segment = 0.5 # seconds
            num_samples = int(sample_rate * duration_per_segment)
            
            # Simulate a few segments
            for i in range(max(1, len(text) // 10)): # More segments for longer text
                 # Generate some dummy audio data (e.g. sine wave)
                frequency = 440 * (i + 1) # Vary frequency for different segments
                t = np.linspace(0, duration_per_segment, num_samples, False, dtype=np.float32)
                audio_segment = 0.3 * np.sin(2 * np.pi * frequency * t)
                yield audio_segment.astype(np.float32)


        def load_voice_embedding(self, voice_name): # Helper for dummy
            main_logger.info(f"DummyKPipeline: Simulating loading voice '{voice_name}'")
            # Simulate a voice embedding: numpy array of shape (1, embedding_dim)
            # Embedding dimension is arbitrary for this dummy
            embedding_dim = 256 
            # Store as if it's [1, D] like some models, or [D]
            # Based on tts.py, pipeline.voices stores the [D] (squeezed) version for mixing
            # but when initially loaded or from some TTS models, it might be [1,D]
            # Let's assume KPipeline internally provides it as [1,D] from self.voices[name]
            # and the mix function expects that, then the final mix is squeezed.
            # For the dummy, let's put [1,D] into self.voices for loaded voices.
            self.voices[voice_name] = np.random.rand(1, embedding_dim).astype(np.float32)


    # Replace KPipeline with DummyKPipeline for the test if kokoro is not available
    # This requires monkeypatching or conditional import if testing directly.
    # For this example, we'll assume we can modify the global KPipeline for the test.
    # This is not ideal for real tests but works for a simple __main__ block.
    
    # --- Monkeypatch KPipeline for example ---
    # Note: This is a global change. In tests, use unittest.mock.patch
    # For this script, it's fine.
    real_KPipeline = KPipeline # Save real one if it exists
    KPipeline = DummyKPipeline # Replace with dummy
    # --- End Monkeypatch ---

    # Now, when TTSEngine calls KPipeline(), it will use DummyKPipeline.
    # We also need to ensure that the dummy pipeline gets its voices loaded.
    # The TTSEngine._load_and_mix_voices calls `list(self.pipeline(".", voice=voice_name, speed=1.0))`
    # which for DummyKPipeline doesn't automatically load voices. We need to manually populate them
    # or make the dummy pipeline smarter.

    # Let's make the dummy pipeline load voices when it's called with a specific voice
    # if that voice isn't already in self.voices.
    original_dummy_call = DummyKPipeline.__call__
    def new_dummy_call(self, text, voice, speed, split_pattern):
        if voice not in self.voices and voice != 'custom_mixed_voice':
            self.load_voice_embedding(voice) # Simulate loading on demand
        yield from original_dummy_call(self, text, voice, speed, split_pattern)
    DummyKPipeline.__call__ = new_dummy_call


    try:
        engine = TTSEngine(
            lang_code="am", 
            voice_config_str="jared50_lex30_extravoice20", 
            voice_mappings={
                "jared": "am_jared_dummy", 
                "lex": "am_lex_dummy",
                "extravoice": "am_extra_dummy"
            },
            tts_speed=1.0,
            logger=main_logger
        )
        
        output_dir = "tts_output_test"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        main_logger.info(f"Test: Synthesizing 'Hello world, this is a test.'")
        path, size = engine.synthesize("test001", "Hello world, this is a test.", output_dir)
        if path and size > 0:
            main_logger.info(f"Test Success: Audio saved to {path}, size {size} bytes.")
        else:
            main_logger.error("Test Failed: Synthesis did not produce a file.")

        main_logger.info(f"Test: Synthesizing 'Another test with multiple lines.\nThis is the second line.'")
        path, size = engine.synthesize("test002", "Another test with multiple lines.\nThis is the second line.", output_dir)
        if path and size > 0:
            main_logger.info(f"Test Success: Audio saved to {path}, size {size} bytes.")
        else:
            main_logger.error("Test Failed: Synthesis did not produce a file for multi-line text.")

        # Test with bad voice config
        main_logger.info("Test: Initializing with bad voice config (name not in mapping)")
        try:
            engine_bad_name = TTSEngine("am", "unknown50_jared50", {"jared": "am_jared_dummy"}, 1.0, main_logger)
        except ValueError as e:
            main_logger.info(f"Test Correctly Caught Error: {e}")

        main_logger.info("Test: Initializing with bad voice config (percentage invalid)")
        try:
            engine_bad_perc = TTSEngine("am", "jaredABC_lex50", {"jared": "am_jared_dummy", "lex": "am_lex_dummy"}, 1.0, main_logger)
        except ValueError as e:
            main_logger.info(f"Test Correctly Caught Error: {e}")
        
        main_logger.info("Test: Initializing with voice config summing to 80% (should normalize)")
        engine_normalize = TTSEngine(
            "am", "jared40_lex40", 
            {"jared": "am_jared_dummy", "lex": "am_lex_dummy"}, 
            1.0, 
            main_logger
        )
        # Check logs for normalization messages.

        main_logger.info("Test: Initializing with voice config summing to 0% (should fail)")
        try:
            engine_zero_sum = TTSEngine(
                "am", "jared0_lex0", 
                {"jared": "am_jared_dummy", "lex": "am_lex_dummy"}, 
                1.0, 
                main_logger
            )
        except ValueError as e:
            main_logger.info(f"Test Correctly Caught Error for zero sum: {e}")


    except Exception as e:
        main_logger.error(f"An error occurred in the TTSEngine example: {e}", exc_info=True)
    finally:
        # Restore KPipeline if it was monkeypatched
        KPipeline = real_KPipeline
        main_logger.info("Restored KPipeline (if it was changed for the example).")
        # Clean up dummy output directory
        # if os.path.exists(output_dir):
        #     import shutil
        #     shutil.rmtree(output_dir)
        #     main_logger.info(f"Cleaned up test output directory: {output_dir}")
        main_logger.info("TTSEngine example finished.")
