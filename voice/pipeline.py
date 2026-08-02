import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.graph import run_pipeline
from voice.tts import synthesize_text
from voice.stt import transcribe_audio

# PRODUCTION PATH EXTENSION:
# -----------------------------------------------------------------------------------------
# While this demo creates a one-off MP3 for a voice script, a real-time production system 
# (e.g., using LiveKit and Twilio SIP Trunking) would look like this:
# 1. Telephony: Twilio routes the SIP call into a LiveKit Room.
# 2. Streaming STT: Swap `faster-whisper` for a streaming STT service (e.g., Deepgram or 
#    Gladia) connected via WebSockets, processing user audio chunks from LiveKit in <300ms.
# 3. LLM Orchestration: Instead of generating the entire script at once, the LLM streams 
#    its response tokens back to the client.
# 4. Streaming TTS: Swap `edge-tts` for a low-latency streaming TTS (e.g., ElevenLabs, PlayHT, 
#    or Cartesia) that synthesizes audio chunks on the fly as LLM tokens arrive.
# 5. Interruption Handling (VAD): If Voice Activity Detection (VAD) triggers while the TTS 
#    is playing, immediately cut off the TTS audio stream and reset the LLM context.
# -----------------------------------------------------------------------------------------

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "calls")

def simulate_call(invoice_id: int):
    print(f"Simulating call for Invoice ID {invoice_id}...")
    
    # Run the orchestrator pipeline to get the voice script
    result = run_pipeline(invoice_id)
    
    if "error" in result:
        print(f"Error generating script: {result['error']}")
        return
        
    drafts = result.get("outputs", {}).get("drafts", {})
    if "error" in drafts:
        print(f"Error drafting script: {drafts['error']}")
        return
        
    voice_script = drafts.get("voice_script_version")
    if not voice_script or voice_script == "N/A":
        print("No voice script was generated.")
        return
        
    print(f"\n[Generated Voice Script]\n{voice_script}\n")
    
    # Save the MP3
    os.makedirs(LOGS_DIR, exist_ok=True)
    filename = f"call_inv{invoice_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    output_path = os.path.join(LOGS_DIR, filename)
    
    print("Synthesizing audio...")
    synthesize_text(voice_script, output_path)
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Voice Call Simulator")
    parser.add_argument("--invoice-id", type=int, required=True, help="Invoice ID to simulate a call for")
    args = parser.parse_args()
    
    simulate_call(args.invoice_id)
