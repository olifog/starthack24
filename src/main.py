import asyncio
from anthropic import AsyncAnthropic
from query import query
import json
from pydub import AudioSegment
from pydub.playback import play
from elevenlabs import generate, stream, play 

anthropic_api_key = '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'

client = AsyncAnthropic(api_key=anthropic_api_key)

system_prompt = open('src/system_prompt.txt', 'r').read()

async def handle_user_message(message):
    """Prompt the LLM with the entire user message, returning a sentence at a time."""
    documents = query(message)

    async with client.messages.stream(
        max_tokens=1024,
        system=system_prompt + "\n\nInformation from the Kanton:" + json.dumps(documents),
        messages=[
            {
                "role": "user",
                "content": message
            }
        ],
        model="claude-3-opus-20240229",
    ) as stream:
        sentence = ''
        async for text in stream.text_stream:
            for c in text:
                sentence += c
                if c in ['.', '!', '?']:
                    yield sentence
                    sentence = ''
        if sentence:
            yield sentence

async def main():
    async for sentence in handle_user_message("Wie melde ich mein Fahrzeug an?"):
        audio=generate(text=sentence, voice="K75lPKuh15SyVhQC1LrE", model="eleven_monolingual_v1", stream=True, api_key="7afd32d708e98824e822491c81d4fb9d")
        stream(audio)
        with open ('output.mp3','wb') as f:
            for i,chunk in enumerate(audio):
                if chunk:
                    f.write(chunk)

asyncio.run(main())
