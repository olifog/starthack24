import gevent
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from gevent import monkey
import urllib
monkey.patch_all()

import os
from openai import OpenAI
import twilio.jwt.access_token
import twilio.jwt.access_token.grants
import twilio.rest
from flask import Flask
from flask_socketio import emit
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Connect, Gather, Stream
from twilio.rest.api.v2010.account.call import CallInstance
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from main3 import handle_user_message, synthesize_audio, analyze_and_delegate
import json
from flask_sockets import Sockets
from gevent.queue import Queue
import base64
import pickle

from twilio.rest import Client

account_sid = "ACd375b4aab3a51dee09a17051ebaffb54"
auth_token  = "0f35cf4ba16a930354e265a83fa7744b"
twilio_client = Client(account_sid, auth_token, region='us1')

load_dotenv()

api_key = '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'
client = OpenAI(api_key=api_key)

system_prompt = open('src/system_prompt.txt', 'r').read()

el_client = ElevenLabs(
    api_key="7afd32d708e98824e822491c81d4fb9d",
)

app = Flask(__name__)
sockets = Sockets(app)

HTTP_SERVER_PORT = 8080

with open('bitte.pkl', 'rb') as f:
    bitte = pickle.load(f)

@app.route("/start_page", methods=['GET', 'POST'])
def start_page():
    print('start_page')
    response = VoiceResponse()
    response.pause(length=1)
    response.play('https://www.olifog.com/start.mp3')
    response.redirect('/gather_speech')
    return str(response)

@app.route("/gather_speech", methods=['GET', 'POST'])
def gather_speech():
    print('gather_speech')
    previous_conversation = request.values.get('previousConversation', '')
    response = VoiceResponse()
    gather = Gather(input='speech', language='de-DE', speechTimeout=3, action=f'/process_speech?{urllib.parse.urlencode({"previousConversation": previous_conversation})}')
    response.append(gather)
    return str(response)

@app.route("/process_speech", methods=['GET', 'POST'])
def process_speech():
    response = VoiceResponse()
    connect = Connect()

    speech_result = request.values.get('SpeechResult', '').lower()
    previous_conversation = request.values.get('previousConversation', '')
    print(f'Processing speech: {speech_result}')

    stream = Stream(
        name="conversation",
        url='wss://43e8-194-209-94-51.ngrok-free.app/conversation',
    )
    stream.parameter(name='speechResult', value=speech_result)
    stream.parameter(name='previousConversation', value=previous_conversation)
    connect.nest(stream)
    response.append(connect)

    print(str(response))
    return str(response)

@sockets.route('/conversation', websocket=True)
def conversation(ws):
    print('connected')

    stream_sid = None
    call_sid = None
    previous_conversation = ''
    text_queue = Queue()
    audio_queue = Queue()
    speech_result = None

    while not ws.closed:
        message = ws.receive()
        if message is None:
            continue
        
        data = json.loads(message)

        if data.get('event') == 'start':
            stream_sid = data.get('streamSid')
            call_sid = data.get('start', {}).get('callSid')
            speech_result = data.get('start', {}).get('customParameters', {}).get('speechResult')
            previous_conversation = data.get('start', {}).get('customParameters', {}).get('previousConversation')
            break
        
    say_bitte = False
    if previous_conversation == '':
        say_bitte = True
    
    previous_conversation += '\n\n' + speech_result
    
    def send_first_message():
        media_payload = {
            "event": "media",
            "streamSid": stream_sid,
            "media": {
                "payload": base64.b64encode(bitte).decode('utf-8')
            }
        }
        ws.send(json.dumps(media_payload))

    def send_audio(aq):
        while True:
            audio = aq.get()
            if audio is None:
                break
            audio = b''.join(audio)
            media_payload = {
                "event": "media",
                "streamSid": stream_sid,
                "media": {
                    "payload": base64.b64encode(audio).decode('utf-8')
                }
            }
            ws.send(json.dumps(media_payload))
        
        ws.send(json.dumps({ 
            "event": "mark",
            "streamSid": stream_sid,
            "mark": {
                "name": "end_of_stream"  
            }
        }))
    
    def wait_for_end():
        while not ws.closed:
            message = ws.receive()
            if message is None:
                continue
            
            data = json.loads(message)

            if data.get('event') == 'stop':
                break
            if data.get('event') == 'mark':
                break
    
    accumulator = []

    greenlets = [
        gevent.spawn(handle_user_message, speech_result, text_queue, previous_conversation, accumulator),
        gevent.spawn(synthesize_audio, text_queue, audio_queue, el_client),
        gevent.spawn(send_audio, audio_queue),
        gevent.spawn(wait_for_end)
    ]

    if say_bitte:
        greenlets.append(gevent.spawn(send_first_message))

    gevent.joinall(greenlets)

    previous_conversation += ''.join(accumulator)

    choice = analyze_and_delegate(previous_conversation)

    if choice == 'continue':
        call = twilio_client.calls.get(call_sid)
        call.update(url=f"https://43e8-194-209-94-51.ngrok-free.app/gather_speech?{urllib.parse.urlencode({'previousConversation': previous_conversation})}", method="POST")


if __name__ == "__main__":
    server = pywsgi.WSGIServer(('', HTTP_SERVER_PORT), app, handler_class=WebSocketHandler)
    print("Server listening on: http://localhost:" + str(HTTP_SERVER_PORT))
    server.serve_forever()
