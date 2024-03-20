import speech_recognition as sr
from openai import OpenAI
import os

# Function to transcribe audio
def transcribe_audio(audio_data):
    api_key = os.environ.get('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key)
    with open("microphone-results.wav", "wb") as f:
        f.write(audio_data.get_wav_data())

    with open("microphone-results.wav", "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=f,
            response_format="text",
            language="de"
        )
        return transcript

# obtain audio from the microphone
r = sr.Recognizer()
p = sr.Microphone()

while True:
    with p as source:
        print("Say something!")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    print("Processing...")
    try:
        transcript = transcribe_audio(audio)
        print(transcript)
    except Exception as e:
        print("Error:", e)