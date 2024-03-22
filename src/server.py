import os
from openai import OpenAI
import twilio.jwt.access_token
import twilio.jwt.access_token.grants
import twilio.rest
from flask import Flask
from flask_sockets import Sockets
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv
from query import query
import json


load_dotenv()

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
api_key = os.environ["TWILIO_API_KEY_SID"]
api_secret = os.environ["TWILIO_API_KEY_SECRET"]
twilio_client = twilio.rest.Client(api_key, api_secret, account_sid)

api_key = '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'
client = OpenAI(api_key=api_key)

system_prompt = open('src/system_prompt.txt', 'r').read()

app = Flask(__name__)
sockets = Sockets(app)

HTTP_SERVER_PORT = 5000
empty_response = 0

@app.route("/start_page", methods=['GET', 'POST'])
def start_page():
    resp = VoiceResponse()
    resp.say('Hallo, wie kann ich Ihnen helfen?', voice='Woman', language='de-DE')
    resp.redirect('/process_speech')
    return str(resp)

@app.route("/hangup", methods=['GET', 'POST'])
def start():
    resp = VoiceResponse()
    resp.hangup()
    return str(resp)

@app.route("/process_speech", methods=['GET', 'POST'])
def process_speech():
    resp = VoiceResponse()

    gather = Gather(input='speech', language='de-DE', speechTimeout=5, action='/gather_speech')
    resp.append(gather)

    return str(resp)

@app.route("/gather_speech", methods=['GET', 'POST'])
def gather_speech():
    """Processes the user's spoken response."""
    # Twilio sends the transcribed speech as text in the 'SpeechResult' parameter
    speech_result = request.values.get('SpeechResult', '').lower()
    resp = VoiceResponse()

    if speech_result.strip() == "":
        empty_response += 1
        if empty_response > 2:
            resp.say('Auf Wiedersehen! Ich wünsche Ihnen einen schönen Tag in St. Gallen!', voice='Woman', language='de-DE')
            resp.redirect('/hangup')
        else:
            resp.redirect('/process_speech')
    else:
        documents = query(speech_result)
        response = client.chat.completions.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt + "\n\nInformation from the Kanton:" + json.dumps(documents),
                },
                {
                    "role": "user",
                    "content": speech_result
                }
            ],
            model="gpt-4",
        )        
        resp.say(response.choices[0].message.content, voice='Woman', language='de-DE')
        resp.redirect('/process_speech')
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
