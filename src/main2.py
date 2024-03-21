import asyncio
from anthropic import AsyncAnthropic
from query import query
import json
from pydub import AudioSegment
from pydub.playback import play
from elevenlabs import stream, play 
from elevenlabs.client import ElevenLabs
import httpx
from openai import AsyncOpenAI

el_client = ElevenLabs(
    api_key="7afd32d708e98824e822491c81d4fb9d",
)

anthropic_api_key = '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'

# client = AsyncAnthropic(api_key=anthropic_api_key)

api_key = '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'
client = AsyncOpenAI(api_key=api_key)

system_prompt = open('src/system_prompt.txt', 'r').read()

async def handle_user_message(message, queue):
    """Prompt the LLM with the entire user message, pushing sentences to a queue."""
    documents = query(message)

    stream = await client.chat.completions.create(
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": system_prompt + "\n\nInformation from the Kanton:" + json.dumps(documents),
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
    async for chunk in stream:
        try:
            for c in chunk.choices[0].delta.content:
                sentence += c
                if c == ' ' and sentence[-2] in ['.', '!', '?']:
                    await queue.put(sentence)  # Push sentences to the queue
                    print("Generated sentence:", sentence)
                    sentence = ''
        except TypeError:
            break
    if sentence:
        await queue.put(sentence)
    await queue.put(None)

async def synthesize_audio(text_queue, audio_queue, el_client):
    while True:
        sentence = await text_queue.get()
        if sentence is None:
            await audio_queue.put(None)
            break
        audio = el_client.generate(text=sentence, voice="K75lPKuh15SyVhQC1LrE", model="eleven_multilingual_v2", stream=True)
        print("Synthesized audio:", sentence)
        await audio_queue.put(audio)  # Push synthesized audio to the queue

async def play_audio(audio_queue):
    while True:
        audio = await audio_queue.get()
        if audio is None:
            break
        print("Playing audio")
        stream(audio)

async def main():
    text_queue = asyncio.Queue()
    audio_queue = asyncio.Queue()

    tasks = [
        asyncio.create_task(handle_user_message("Wie melde ich mein Fahrzeug an?", text_queue)),
        asyncio.create_task(synthesize_audio(text_queue, audio_queue, el_client)),
        asyncio.create_task(play_audio(audio_queue)),
    ]

    await asyncio.gather(*tasks)

asyncio.run(main())
