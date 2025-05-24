import pytest
from unittest.mock import patch, MagicMock, PropertyMock, call
import numpy as np # For dummy embeddings

# Import the class to be tested
from tts_server.tts_engine import TTSEngine

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
def voice_mappings():
    return {"jared": "am_jared_kokoro", "martha": "am_martha_kokoro"}

# --- Tests for _parse_voice_config ---

def test_parse_voice_config_valid(voice_mappings):
    """Test _parse_voice_config with valid input."""
    # Patch KPipeline within the tts_engine module for the scope of this test
    # This avoids needing KPipeline to be available at all.
    with patch('tts_server.tts_engine.KPipeline', MagicMock()):
        engine = TTSEngine(lang_code="am", voice_config_str="jared50_martha50", 
                           voice_mappings=voice_mappings, tts_speed=1.0)
    
    # Directly test the private method (usually not recommended, but for complex internal logic it can be useful)
    # Or, test its effects via the constructor if it's simple enough.
    # Here, parsing is complex enough to warrant a direct, focused test.
    parsed = engine._parse_voice_config("jared50_martha50", voice_mappings)
    assert parsed == [("am_jared_kokoro", 0.5), ("am_martha_kokoro", 0.5)]

    parsed_single = engine._parse_voice_config("jared100", voice_mappings)
    assert parsed_single == [("am_jared_kokoro", 1.0)]
    
    parsed_complex_names = engine._parse_voice_config("voice_name_long60_another_voice40", 
                                                     {"voice_name_long": "internal_long", "another_voice": "internal_short"})
    assert parsed_complex_names == [("internal_long", 0.6), ("internal_short", 0.4)]


def test_parse_voice_config_normalization(voice_mappings):
    """Test _parse_voice_config with percentages not summing to 100 (normalization)."""
    with patch('tts_server.tts_engine.KPipeline', MagicMock()):
        engine = TTSEngine(lang_code="am", voice_config_str="jared40_martha40", # Sums to 80%
                           voice_mappings=voice_mappings, tts_speed=1.0)
    
    # Accessing the method after init, voice_config_str in init is different from test.
    # This tests the method in isolation.
    parsed = engine._parse_voice_config("jared40_martha40", voice_mappings) 
    # Expected: [("am_jared_kokoro", 0.4/0.8 = 0.5), ("am_martha_kokoro", 0.4/0.8 = 0.5)]
    assert len(parsed) == 2
    assert parsed[0][0] == "am_jared_kokoro"
    assert parsed[1][0] == "am_martha_kokoro"
    assert abs(parsed[0][1] - 0.5) < 1e-9
    assert abs(parsed[1][1] - 0.5) < 1e-9
    assert abs(sum(p[1] for p in parsed) - 1.0) < 1e-9 # Sum should be 1.0

    # Test with a single voice, not 100% (e.g. jared50)
    parsed_single_norm = engine._parse_voice_config("jared50", voice_mappings)
    assert len(parsed_single_norm) == 1
    assert parsed_single_norm[0][0] == "am_jared_kokoro"
    assert abs(parsed_single_norm[0][1] - 1.0) < 1e-9 # Should normalize to 100%

def test_parse_voice_config_name_not_in_mappings(voice_mappings):
    """Test _parse_voice_config with a name not in voice_mappings."""
    with patch('tts_server.tts_engine.KPipeline', MagicMock()):
        engine = TTSEngine(lang_code="am", voice_config_str="jared100", # Valid init
                           voice_mappings=voice_mappings, tts_speed=1.0)
    
    with pytest.raises(ValueError) as excinfo:
        engine._parse_voice_config("unknown_voice50_jared50", voice_mappings)
    assert "Voice name 'unknown_voice' not found in mappings" in str(excinfo.value)

def test_parse_voice_config_invalid_format(voice_mappings):
    """Test _parse_voice_config with invalid format string."""
    with patch('tts_server.tts_engine.KPipeline', MagicMock()):
        engine = TTSEngine(lang_code="am", voice_config_str="jared100", # Valid init
                           voice_mappings=voice_mappings, tts_speed=1.0)

    with pytest.raises(ValueError) as excinfo:
        engine._parse_voice_config("jaredNO_NUMBER", voice_mappings)
    assert "Invalid format in voice part 'jaredNO_NUMBER'" in str(excinfo.value) or \
           "Could not separate name and percentage" in str(excinfo.value) # Depending on exact failure point

    with pytest.raises(ValueError) as excinfo:
        engine._parse_voice_config("100jared", voice_mappings) # Number first
    assert "Invalid format in voice part '100jared'" in str(excinfo.value) or \
           "Could not separate name and percentage" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        engine._parse_voice_config("", voice_mappings) # Empty string
    assert "Voice configuration string cannot be empty" in str(excinfo.value)


# --- Tests for TTSEngine Initialization ---

@patch('tts_server.tts_engine.TTSEngine._load_and_mix_voices') # Mock this method for init tests
@patch('tts_server.tts_engine.TTSEngine._parse_voice_config')
def test_tts_engine_initialization_calls(mock_parse_config, mock_load_mix, mock_kpipeline_class, voice_mappings):
    """Test that TTSEngine initialization calls helper methods."""
    
    # Return a valid parsed structure from the mock
    mock_parse_config.return_value = [("am_jared_kokoro", 1.0)] 
    
    with patch('tts_server.tts_engine.KPipeline', mock_kpipeline_class):
        engine = TTSEngine(
            lang_code="am",
            voice_config_str="jared100",
            voice_mappings=voice_mappings,
            tts_speed=1.0
        )

    mock_kpipeline_class.assert_called_once_with(lang_code="am")
    mock_parse_config.assert_called_once_with("jared100", voice_mappings)
    mock_load_mix.assert_called_once_with([("am_jared_kokoro", 1.0)])
    assert engine.tts_speed == 1.0


# --- Test for _load_and_mix_voices (more involved) ---
# This method interacts heavily with the (mocked) KPipeline instance.

def test_load_and_mix_voices(mock_kpipeline_instance, voice_mappings):
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
            # For this test, init's voice_config_str doesn't matter as much as the direct call below
            voice_config_str="jared100", 
            voice_mappings=voice_mappings, 
            tts_speed=1.0
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
        # We can mock it if its details are not relevant to synthesize testing.
        with patch.object(TTSEngine, '_load_and_mix_voices', MagicMock()):
            engine = TTSEngine("am", "jared100", voice_mappings, 1.0)
    
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
