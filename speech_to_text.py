import asyncio
import websockets
import pyaudio
import json
import time
from datetime import datetime
from deepgram import Deepgram
import os

DEEPGRAM_API_KEY = "1"

SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_SIZE = 1024
LANGUAGE = "en"

async def stream_audio():
    """Stream audio from the microphone to Deepgram for real-time transcription."""

    # Initialize PyAudio for microphone input
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    # Prepare URL for Deepgram's real-time transcription endpoint
    deepgram_url = f"wss://api.deepgram.com/v1/listen?language={LANGUAGE}"

    # WebSocket headers with API key
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}"
    }

    # Connect to Deepgram WebSocket
    async with websockets.connect(deepgram_url, extra_headers=headers) as ws:
        print("🎙️ Listening for speech... Press Ctrl+C to stop.")

        # Open a file to log transcriptions
        log_file = "deepgram_transcription.txt"
        with open(log_file, "a") as f:

            try:
                while True:
                    # Capture audio from the microphone
                    audio_chunk = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    await ws.send(audio_chunk)

                    # Check for responses
                    response = await ws.recv()
                    response_data = json.loads(response)

                    # Check if transcript exists
                    if 'channel' in response_data and 'alternatives' in response_data['channel']:
                        transcript = response_data['channel']['alternatives'][0]['transcript']
                        if transcript:
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            print(f"[{timestamp}] {transcript}")

                            # Write to the log file
                            f.write(f"[{timestamp}] {transcript}\n")

            except KeyboardInterrupt:
                print("🛑 Stopping the real-time transcription...")
                stream.stop_stream()
                stream.close()
                p.terminate()

            except Exception as e:
                print(f"❌ Error: {e}")

    print("✅ Transcription complete. Check 'deepgram_transcription.txt' for the logs.")


# Run the asynchronous event loop
if __name__ == "__main__":
    asyncio.run(stream_audio())