from pvrecorder import PvRecorder
import wave
import struct
import time
import speech_recognition as sr
import google.generativeai as genai
import os
from dotenv import load_dotenv



load_dotenv()
# Configuration
device_index = -1  # Use default microphone
frame_length = 512  # 32ms of 16kHz audio
output_file = "recording.wav"
record_seconds = 5  # Duration to record in seconds
geminikey = os.getenv("GOOGLE_API_KEY")

# Initialize recorder
recorder = PvRecorder(frame_length=frame_length, device_index=device_index)
#gemini_api_key = os.environ.get(geminikey) 
genai.configure(api_key=geminikey)  
model = genai.GenerativeModel('gemini-pro')

try:
    recorder.start()
    print(f"Recording for {record_seconds} seconds...")
    
    frames = []
    start_time = time.time()
    while time.time() - start_time < record_seconds:
        frame = recorder.read()
        frames.extend(frame)

    print("Recording complete!")

finally:
    recorder.stop()
    recorder.delete()

    # Save to WAV file
    with wave.open(output_file, 'w') as f:
        f.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
        f.writeframes(struct.pack("h" * len(frames), *frames))

print(f"Audio saved to {output_file}")
r=sr.Recognizer()
with sr.AudioFile("recording.wav") as source:
    audio = r.record(source)
try:
    s = r.recognize_google(audio)
    prompt = f"split it into sentences:\n{s}"
    start=model.generate_content(f"extract start time:\n{s}")
    end=model.generate_content(f"extract end time:\n{s}")
    desc=model.generate_content(f"extract whatever you get except start and the end time:\n{s}")
    summary=model.generate_content(f"summarize:\n{s}")

    #response = model.generate_content(prompt)
    #print(f"Transcribed message: {response.text}")
    #print(f"Start Response: {start.candidates[0].content.parts[0].text}")
    #print(f"End Response: {end.candidates[0].content.parts[0].text}")
    #print(f"Description Response: {desc.candidates[0].content.parts[0].text}")
    print(f"summary:{summary.candidates[0].content.parts[0].text}")

except sr.UnknownValueError:
    print("Could not understand audio")
    #print("Text: "+s)
except Exception as e:
    print("Exception: "+str(e))


