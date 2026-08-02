import os

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

def transcribe_audio(audio_path: str, model_size="base") -> str:
    """
    Transcribes an audio file to text using faster-whisper.
    Runs locally on CPU by default.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
    if WhisperModel is None:
        raise ImportError("faster-whisper is not installed. Run: pip install faster-whisper")
        
    # Run on CPU with int8 quantization for speed on local machines
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    segments, info = model.transcribe(audio_path, beam_size=5)
    
    print(f"Detected language '{info.language}' with probability {info.language_probability}")
    
    text = ""
    for segment in segments:
        text += segment.text + " "
        
    return text.strip()
