from litellm import completion
from openai import OpenAI
import speech_recognition as sr
import elevenlabs
from elevenlabs import generate, stream
elevenlabs.api_key="7afd32d708e98824e822491c81d4fb9d"
r = sr.Recognizer()
p = sr.Microphone()
api_key = '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'
client = OpenAI(api_key=api_key)
silent_count = 0
turn = 0

system_prompt = {
    'role': 'system', 
    'content': 'You are being used as a voice chatbot for the St Gallen governnment, primarily for old people. If they ask for passport replacement can you type the text the sytem will soon redirect them to +49 30 5000 2000. You are a human assistant. You want to respond quickly. You are helpful and friendly. If they say they need tax advice tell them the system will soon direct them to the tax department. Most Importantly be concise, friendly, ask if they want a repeat and dont give false information. Ask them if they want a repeat and if they say yes just REPEAT exactly what you said. You only say things you are sure about.'
}

history = []
answer = ""
def generate2(messages):
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
silence_threshold = 0.6  # Seconds of silence before stopping recording

while True:
    print("Start speaking.")
    with p as source:
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = silence_threshold
        if turn == 0:
            audio2=generate(text="Hello welcome to the Canton of St.Gallon, how can I help you today?", voice="K75lPKuh15SyVhQC1LrE", model="eleven_monolingual_v1", stream=True, api_key="7afd32d708e98824e822491c81d4fb9d")
            stream(audio2)
        audio = r.listen(p)
    # Transcribe recording using whisper
    print("done")
    with open("microphone-results.wav", 'wb') as wf:
        wf.write(audio.get_wav_data())
    with open("microphone-results.wav", "rb") as wf:
        user_text = client.audio.transcriptions.create(
            model="whisper-1", 
            file=wf,
            response_format="text",
            language="de"
        )
        if user_text.strip() == "":
            if silent_count == 3:
                break
            silent_count += 1
            audio=generate(text="Hey, is there anything more I could help you with?", voice="Nicole", model="eleven_monolingual_v1", stream=True, api_key="7afd32d708e98824e822491c81d4fb9d")
            stream(audio)
            continue
        print(f'>>>{user_text}\n<<< ', end="", flush=True)
        history.append({'role': 'user', 'content': user_text})

        # Generate and stream output
        generator = generate2(history[-10:]+[system_prompt])
        audio=generate(text=generator, voice="K75lPKuh15SyVhQC1LrE", model="eleven_monolingual_v1", stream=True, api_key="7afd32d708e98824e822491c81d4fb9d")
        stream(audio)
        with open ('output.mp3','wb') as f:
            for i,chunk in enumerate(audio):
                if chunk:
                    f.write(chunk)
    history.append({'role': 'assistant', 'content': answer})