import asyncio
from anthropic import AsyncAnthropic
from query import query
import json

anthropic_api_key = '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'

client = AsyncAnthropic(api_key=anthropic_api_key)

system_prompt = open('src/system_prompt.txt', 'r').read()

async def handle_user_message(message):
    """Prompt the LLM with the entire user message, returning a sentence at a time."""
    documents = query(message)

    async with client.messages.stream(
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": message + "\n\nRelevant information you know:\n" + json.dumps(documents),
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
    async for sentence in handle_user_message("Informationen zum Ersatz von Reisepässen"):
        print(sentence)

asyncio.run(main())
