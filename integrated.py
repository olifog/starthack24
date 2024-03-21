from litellm import completion
from openai import OpenAI
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play


r = sr.Recognizer()
p = sr.Microphone()
api_key = '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'
client = OpenAI(api_key=api_key)

system_prompt = {
    'role': 'system', 
    'content': 'You are a human assistant. You want to respond quickly. You are helpful. You do not hallucinate.'
}

history = []
answer = ""
def generate(messages):
    global answer
    answer = ""
    for chunk in completion(
    max_tokens=512,
    messages=messages,
    model="claude-3-opus-20240229",
    stream=True,
    api_key='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',
    ):
        if (text_chunk := chunk["choices"][0]["delta"].get("content")):
            answer += text_chunk
            yield text_chunk
silence_threshold = 1  # Seconds of silence before stopping recording

while True:
    print("Start speaking.")

    with p as source:
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = silence_threshold
        audio = r.listen(p)
    # Transcribe recording using whisper
    with open("microphone-results.wav", 'wb') as wf:
        wf.write(audio.get_wav_data())
    with open("microphone-results.wav", "rb") as wf:
        user_text = client.audio.transcriptions.create(
            model="whisper-1", 
            file=wf,
            response_format="text",
            language="en"
        )
        print(f'>>>{user_text}\n<<< ', end="", flush=True)
        # history.append({'role': 'user', 'content': user_text})
        x= {'role': 'user', 'content': user_text}

        # Generate and stream output
        generator = generate([system_prompt] + [x])
        generator_string = ''.join(generator)
        response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=generator_string,
        )
        response.stream_to_file("speech.mp3")
        sound = AudioSegment.from_mp3("speech.mp3")
        play(sound)
        # history.append({'role': 'assistant', 'content': answer})
