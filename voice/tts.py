import os
import asyncio

def synthesize_text(text: str, output_path: str):
    """
    Synthesizes text into speech and saves to an MP3 file.
    Uses edge-tts if available, otherwise falls back to gTTS.
    """
    # Create parent directories if they don't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    try:
        import edge_tts
        
        async def _synthesize():
            # Using a friendly, professional voice
            voice = "en-US-ChristopherNeural"
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            
        asyncio.run(_synthesize())
        print(f"Successfully synthesized with edge-tts: {output_path}")
        
    except ImportError:
        print("edge-tts not found, falling back to gTTS...")
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            print(f"Successfully synthesized with gTTS: {output_path}")
        except ImportError:
            raise ImportError("Neither edge-tts nor gTTS is installed. Please install one of them.")
