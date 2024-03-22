import asyncio
from concurrent.futures import ThreadPoolExecutor
import queue  # Using the synchronous Queue since we're in a threaded context
from anthropic import AsyncAnthropic
from query import query
import json
from pydub import AudioSegment
from pydub.playback import play
from elevenlabs import stream, play 
from elevenlabs.client import ElevenLabs
import httpx
from openai import OpenAI

el_client = ElevenLabs(
    api_key="7afd32d708e98824e822491c81d4fb9d",
)

anthropic_api_key = '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'

api_key = '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'
client = OpenAI(api_key=api_key)

system_prompt = open('src/system_prompt.txt', 'r').read()

def get_audio_duration(audio):
    bitrate_kbps = 128
    bitrate_bps = bitrate_kbps * 1000

    audio_length_seconds = (len(audio) * 8) / bitrate_bps
    return audio_length_seconds

def handle_user_message(message, queue):
    """Prompt the LLM with the entire user message, pushing sentences to a queue."""
    documents = query(message)

    stream = client.chat.completions.create(
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": system_prompt + "\n\nInformation from the Kanton:" + json.dumps(documents)[:2*6000],
            },
            {
                "role": "user",
                "content": message
            }
        ],
        model="gpt-4",
        stream=True
    )

    sentence = ''
    for chunk in stream:
        try:
            for c in chunk.choices[0].delta.content:
                sentence += c
                if c == ' ' and sentence[-2] in ['.', '!', '?']:
                    queue.put(sentence)  # Push sentences to the queue
                    print("Generated sentence:", sentence)
                    sentence = ''
        except TypeError:
            break
    if sentence:
        queue.put(sentence)
    queue.put(None)

def synthesize_audio(text_queue, audio_queue, el_client):
    """Synthesize audio from text and push it to another queue."""
    while True:
        sentence = text_queue.get()
        if sentence is None:
            audio_queue.put(None)
            break
        audio = el_client.generate(text=sentence, voice="K75lPKuh15SyVhQC1LrE", model="eleven_multilingual_v2", stream=True, output_format="ulaw_8000")
        print("Synthesized audio:", sentence)
        audio_queue.put(audio)

def play_audio(audio_queue):
    """Play audio from the queue."""
    while True:
        audio = audio_queue.get()
        if audio is None:
            break
        print("Playing audio")
        stream(audio)

def main():
    text_queue = queue.Queue()
    audio_queue = queue.Queue()

    print("STARTING!!!!!")

    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(handle_user_message, "Wie melde ich mein Fahrzeug an?", text_queue)
        executor.submit(synthesize_audio, text_queue, audio_queue, el_client)
        executor.submit(play_audio, audio_queue)

if __name__ == "__main__":
    main()
