import pytest
import os # Add import os
from unittest.mock import patch, MagicMock, PropertyMock, call
import numpy as np # For dummy embeddings

# Import the class to be tested - MOVED INTO TESTS
# from tts_server.tts_engine import TTSEngine

# Mock KPipeline before it's imported by tts_engine module
# This requires careful handling if tts_engine is already imported elsewhere.
# For pytest, it's common to patch at the point of use in the module under test.

@pytest.fixture
def mock_kpipeline_instance():
    """Provides a mock instance of KPipeline."""
    instance = MagicMock()
    instance.voices = {} # Mock the voices dictionary
    # Mock the __call__ method to be a generator, like the real KPipeline
    instance.return_value = iter([np.array([0.1, 0.2], dtype=np.float32)]) # Dummy audio segment
    return instance

@pytest.fixture
def mock_kpipeline_class(mock_kpipeline_instance):
    """Provides a mock KPipeline class that returns mock_kpipeline_instance."""
    klass = MagicMock(return_value=mock_kpipeline_instance)
    return klass

@pytest.fixture
def voice_mappings(): # Updated fixture
    return {
        "adam": "kokoro_adam", 
        "michael": "kokoro_michael", 
        "jared": "kokoro_jared", 
        "lex": "kokoro_lex"
    }

# --- Tests for _parse_voice_config ---

def test_parse_voice_config_valid(voice_mappings):
    from tts_server.tts_engine import TTSEngine # Import here
    """Test _parse_voice_config with valid input, sum = 100%."""
    with patch('tts_server.tts_engine.KPipeline', MagicMock()):
        # Pass default_voice_friendly_name, though it shouldn't be used here
        engine = TTSEngine(lang_code="am", voice_config_str="jared50_lex50", 
                           voice_mappings=voice_mappings, tts_speed=1.0,
                           default_voice_friendly_name="adam") 
    
    # Test direct call to _parse_voice_config
    # Scenario: Sum is 100%
    parsed = engine._parse_voice_config("jared50_lex50", voice_mappings, default_voice_friendly_name="adam")
    # Using set for order-agnostic comparison
    assert set(parsed) == {("kokoro_jared", 0.5), ("kokoro_lex", 0.5)}

    # Scenario: Single voice at 100%
    parsed_single = engine._parse_voice_config("jared100", voice_mappings, default_voice_friendly_name="adam")
    assert parsed_single == [("kokoro_jared", 1.0)]
    
    # Scenario: Complex names, sum is 100%
    custom_mappings = {"voice_name_long": "internal_long", "another_voice": "internal_short", "adam": "kokoro_adam"}
    parsed_complex_names = engine._parse_voice_config(
        "voice_name_long60_another_voice40", 
        custom_mappings,
        default_voice_friendly_name="adam"
    )
    assert set(parsed_complex_names) == {("internal_long", 0.6), ("internal_short", 0.4)}


def test_parse_voice_config_normalization_sum_greater_than_100(voice_mappings):
    from tts_server.tts_engine import TTSEngine # Import here
    """Test _parse_voice_config normalization when sum of percentages > 100%."""
    with patch('tts_server.tts_engine.KPipeline', MagicMock()):
        engine = TTSEngine(lang_code="am", voice_config_str="jared80_lex80", # Sums to 160%
                           voice_mappings=voice_mappings, tts_speed=1.0,
                           default_voice_friendly_name="adam")
    
    parsed = engine._parse_voice_config("jared80_lex80", voice_mappings, default_voice_friendly_name="adam") 
    # Expected: [("kokoro_jared", 0.8/1.6 = 0.5), ("kokoro_lex", 0.8/1.6 = 0.5)]
    assert len(parsed) == 2
    # Sort for consistent order before checking elements if order matters for specific checks
    parsed.sort() 
    assert parsed[0][0] == "kokoro_jared" # Assuming alphabetical sort: jared before lex
    assert parsed[1][0] == "kokoro_lex"
    assert abs(parsed[0][1] - 0.5) < 1e-9
    assert abs(parsed[1][1] - 0.5) < 1e-9
    assert abs(sum(p[1] for p in parsed) - 1.0) < 1e-9

    # Test with a single voice > 100% (e.g. jared150)
    parsed_single_norm = engine._parse_voice_config("jared150", voice_mappings, default_voice_friendly_name="adam")
    assert len(parsed_single_norm) == 1
    assert parsed_single_norm[0][0] == "kokoro_jared"
    assert abs(parsed_single_norm[0][1] - 1.0) < 1e-9 # Should normalize to 1.0

def test_parse_voice_config_name_not_in_mappings(voice_mappings):
    from tts_server.tts_engine import TTSEngine # Import here
    """Test _parse_voice_config with a name not in voice_mappings."""
    with patch('tts_server.tts_engine.KPipeline', MagicMock()):
        engine = TTSEngine(lang_code="am", voice_config_str="jared100", 
                           voice_mappings=voice_mappings, tts_speed=1.0,
                           default_voice_friendly_name="adam")
    
    with pytest.raises(ValueError, match="Voice name 'unknown_voice' not found in mappings"):
        engine._parse_voice_config("unknown_voice50_jared50", voice_mappings, default_voice_friendly_name="adam")

def test_parse_voice_config_invalid_format(voice_mappings):
    from tts_server.tts_engine import TTSEngine # Import here
    """Test _parse_voice_config with invalid format string."""
    with patch('tts_server.tts_engine.KPipeline', MagicMock()):
        engine = TTSEngine(lang_code="am", voice_config_str="jared100", 
                           voice_mappings=voice_mappings, tts_speed=1.0,
                           default_voice_friendly_name="adam")

    with pytest.raises(ValueError, match="Invalid format in voice part 'jaredNO_NUMBER'"):
        engine._parse_voice_config("jaredNO_NUMBER", voice_mappings, default_voice_friendly_name="adam")
    
    with pytest.raises(ValueError, match="Invalid format in voice part '100jared'"):
        engine._parse_voice_config("100jared", voice_mappings, default_voice_friendly_name="adam")
    
    # Note: The case for "" (empty string) is now handled by default voice logic if a default voice is provided.
    # If no default voice and empty string, it should raise ValueError.
    # This specific test for "Voice configuration string cannot be empty" might need to be in the new default logic tests.
    # For now, let's assume default_voice_friendly_name="adam" is passed.
    # The new logic: empty string + default voice = default voice 100%.
    # So, this specific old test for empty string error message is no longer valid as is.
    # It will be covered by the new test_parse_voice_config_default_logic.


# --- New Tests for Default Voice Logic ---
@pytest.mark.parametrize("config_str, default_name, expected_kokoro_mix, error_type, error_match", [
    # Scenario 1: Sum < 100%
    ("michael40", "adam", [("kokoro_michael", 0.4), ("kokoro_adam", 0.6)], None, None),
    # Scenario 2: Empty config string
    ("", "adam", [("kokoro_adam", 1.0)], None, None),
    # Scenario 3: Default voice also in config (sum < 100%)
    ("adam10_michael30", "adam", [("kokoro_michael", 0.3), ("kokoro_adam", 0.7)], None, None), # 0.1 explicit + 0.6 remainder
    # Scenario 4: Error - Default voice not in mappings
    ("michael40", "unknown_default", None, ValueError, "Default voice 'unknown_default' not found in voice mappings."),
    # Scenario 5: Error - Default voice needed (empty config) but not provided to parser
    ("", None, None, ValueError, "Default voice must be specified when voice_config_str sums to 0% or is empty."),
    # Scenario 6: Error - Default voice needed (sum < 100%) but not provided
    ("michael30", None, None, ValueError, "Default voice must be specified when voice_config_str sums to less than 100%."),
    # Scenario 7: Sum is 0%, default voice used
    ("michael0_jared0", "adam", [("kokoro_adam", 1.0)], None, None),
])
def test_parse_voice_config_default_logic(
    config_str, default_name, expected_kokoro_mix, error_type, error_match, voice_mappings
):
    from tts_server.tts_engine import TTSEngine # Import here
    with patch('tts_server.tts_engine.KPipeline', MagicMock()):
        # Create a base engine instance; specific config string isn't vital here as we call _parse_voice_config directly.
        engine = TTSEngine(lang_code="am", voice_config_str="adam100", # A valid dummy config for init
                           voice_mappings=voice_mappings, tts_speed=1.0,
                           default_voice_friendly_name="adam") # Default for engine instance

    if error_type:
        with pytest.raises(error_type, match=error_match):
            engine._parse_voice_config(config_str, voice_mappings, default_name)
    else:
        parsed = engine._parse_voice_config(config_str, voice_mappings, default_name)
        # Using set for order-agnostic comparison of tuples
        assert set(parsed) == set(expected_kokoro_mix)
        # Also check sum is 1.0 for valid cases
        assert abs(sum(ratio for _, ratio in parsed) - 1.0) < 1e-9


# --- Tests for TTSEngine Initialization ---

@patch('tts_server.tts_engine.TTSEngine._load_and_mix_voices')
@patch('tts_server.tts_engine.TTSEngine._parse_voice_config')
def test_tts_engine_initialization_calls(mock_parse_config, mock_load_mix, mock_kpipeline_class, voice_mappings):
    from tts_server.tts_engine import TTSEngine
    """Test that TTSEngine initialization calls helper methods."""
    mock_parse_config.return_value = [("kokoro_jared", 1.0)] 
    
    with patch('tts_server.tts_engine.KPipeline', mock_kpipeline_class):
        engine = TTSEngine(
            lang_code="am",
            voice_config_str="jared100",
            voice_mappings=voice_mappings,
            tts_speed=1.0,
            default_voice_friendly_name="adam" # Added
        )

    mock_kpipeline_class.assert_called_once_with(lang_code="am")
    # Check that default_voice_friendly_name is passed to _parse_voice_config
    mock_parse_config.assert_called_once_with("jared100", voice_mappings, "adam")
    mock_load_mix.assert_called_once_with([("kokoro_jared", 1.0)])
    assert engine.tts_speed == 1.0


# --- Test for _load_and_mix_voices (more involved) ---
# This method interacts heavily with the (mocked) KPipeline instance.

def test_load_and_mix_voices(mock_kpipeline_instance, voice_mappings):
    from tts_server.tts_engine import TTSEngine # Import here
    """Test the _load_and_mix_voices method."""

    # Prepare the KPipeline mock instance
    # Simulate voice embeddings: numpy array of shape (1, embedding_dim)
    embedding_dim = 3 # Small for testing
    jared_emb = np.array([[1, 2, 3]], dtype=np.float32)
    martha_emb = np.array([[4, 5, 6]], dtype=np.float32)

    # This mock assumes that when pipeline is called with a voice name,
    # it "loads" it into its .voices dict if not present.
    # The TTSEngine._load_and_mix_voices expects `pipeline.voices[name]` to exist
    # after the pre-loading call: `list(self.pipeline(".", voice=voice_name, speed=1.0))`
    
    def pipeline_call_effect(text, voice, speed, split_pattern=None): # Added split_pattern for compatibility
        # If pre-loading, simulate adding the voice embedding to the pipeline's voice dict
        if voice == "am_jared_kokoro" and "am_jared_kokoro" not in mock_kpipeline_instance.voices:
            mock_kpipeline_instance.voices["am_jared_kokoro"] = jared_emb
        elif voice == "am_martha_kokoro" and "am_martha_kokoro" not in mock_kpipeline_instance.voices:
            mock_kpipeline_instance.voices["am_martha_kokoro"] = martha_emb
        # Return dummy audio segment generator
        yield np.array([0.1], dtype=np.float32) 

    mock_kpipeline_instance.side_effect = pipeline_call_effect # For calls like self.pipeline(...)
    
    # We need to patch KPipeline class for instantiation, and then use the prepared instance
    with patch('tts_server.tts_engine.KPipeline', return_value=mock_kpipeline_instance):
        engine = TTSEngine(
            lang_code="am", 
            voice_config_str="jared100", 
            voice_mappings=voice_mappings, 
            tts_speed=1.0,
            default_voice_friendly_name="adam" # Added
        )

        # Now directly call _load_and_mix_voices with specific parsed data
        parsed_data_for_mixing = [("am_jared_kokoro", 0.5), ("am_martha_kokoro", 0.5)]
        engine._load_and_mix_voices(parsed_data_for_mixing)

    # Assertions:
    # 1. Pre-loading calls were made for each unique voice
    #    The pipeline_call_effect simulates loading, so we check .voices dict
    assert "am_jared_kokoro" in mock_kpipeline_instance.voices
    assert "am_martha_kokoro" in mock_kpipeline_instance.voices
    
    # 2. A 'custom_mixed_voice' was added to the pipeline's voices
    assert 'custom_mixed_voice' in mock_kpipeline_instance.voices
    
    # 3. The mixed embedding is correct
    #    Expected: (jared_emb * 0.5) + (martha_emb * 0.5)
    #    The TTSEngine's _load_and_mix_voices might squeeze the final embedding.
    #    If jared_emb is [1,3], then jared_emb * 0.5 is [[0.5, 1.0, 1.5]]
    #    martha_emb * 0.5 is [[2.0, 2.5, 3.0]]
    #    Sum is [[2.5, 3.5, 4.5]]
    #    If squeezed, it becomes [2.5, 3.5, 4.5]
    
    expected_mixed_emb_squeezed = (jared_emb.squeeze(0) * 0.5) + (martha_emb.squeeze(0) * 0.5)
    
    # Check the shape and content of the stored custom_mixed_voice
    # The TTSEngine code has: `final_mixed_emb = mixed_voice_emb.squeeze(0)` if ndim > 1
    # So, we expect the stored embedding to be 1D.
    stored_mixed_emb = mock_kpipeline_instance.voices['custom_mixed_voice']
    assert stored_mixed_emb.ndim == 1 
    np.testing.assert_array_almost_equal(stored_mixed_emb, expected_mixed_emb_squeezed, decimal=7)


# --- Test for synthesize method ---
@patch('tts_server.tts_engine.sf') # Mock soundfile
@patch('tts_server.tts_engine.os.path.exists')
@patch('tts_server.tts_engine.os.makedirs')
@patch('tts_server.tts_engine.os.path.getsize')
def test_synthesize_successful(mock_getsize, mock_makedirs, mock_path_exists, mock_sf, 
                               mock_kpipeline_instance, voice_mappings):
    from tts_server.tts_engine import TTSEngine # Import here
    """Test the synthesize method for a successful case."""

    # Setup KPipeline mock for synthesis
    dummy_audio_segment = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    # This mock is for the pipeline instance used by the engine.
    # It should yield audio segments when called.
    mock_kpipeline_instance.reset_mock() # Reset from previous tests if any
    mock_kpipeline_instance.side_effect = None # Clear previous side_effect
    mock_kpipeline_instance.return_value = iter([dummy_audio_segment]) # __call__ returns iterator

    # Assume 'custom_mixed_voice' is already in pipeline.voices (e.g. by _load_and_mix_voices)
    # For this test, we don't need the actual embedding, just the key.
    mock_kpipeline_instance.voices['custom_mixed_voice'] = np.array([1,2,3]) # Dummy, not used by this mock

    with patch('tts_server.tts_engine.KPipeline', return_value=mock_kpipeline_instance):
        # Initialize engine - _load_and_mix_voices will be called.
        # We need TTSEngine for patch.object target.
        # The mock_global_kokoro_module in conftest.py *must* be effective here.
        with patch.object(TTSEngine, '_load_and_mix_voices', MagicMock()): # TTSEngine needs to be resolvable
            engine = TTSEngine("am", "jared100", voice_mappings, 1.0, default_voice_friendly_name="adam") # Added
    
    mock_path_exists.return_value = True # Assume output directory exists or is created
    mock_getsize.return_value = 12345 # Dummy file size

    output_dir = "test_audio_out"
    msg_id = "test_msg_001"
    text = "Hello world"
    
    expected_output_path = os.path.join(output_dir, f"message_{msg_id}.wav")

    path, size = engine.synthesize(msg_id, text, output_dir)

    assert path == expected_output_path
    assert size == 12345

    # Check KPipeline was called correctly for synthesis
    mock_kpipeline_instance.assert_called_once_with(
        text, 
        voice='custom_mixed_voice', 
        speed=1.0,
        split_pattern=r'\n+'
    )
    # Check soundfile.write was called correctly
    mock_sf.write.assert_called_once_with(expected_output_path, dummy_audio_segment, samplerate=24000)
    mock_getsize.assert_called_once_with(expected_output_path)


if __name__ == "__main__":
    pytest.main()
