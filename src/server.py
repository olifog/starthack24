import base64
import json
import logging
import os
import twilio.jwt.access_token
import twilio.jwt.access_token.grants
import twilio.rest
from flask import Flask
from flask_sockets import Sockets
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv

load_dotenv()

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
api_key = os.environ["TWILIO_API_KEY_SID"]
api_secret = os.environ["TWILIO_API_KEY_SECRET"]
twilio_client = twilio.rest.Client(api_key, api_secret, account_sid)

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
    # Start our TwiML response
    resp = VoiceResponse()

    # Start our <Gather> verb
    gather = Gather(input='speech', language='de',speechTimeout=3, action='/gather_speech')
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
            resp.say("Ich habe nichts gehört. Bitte versuchen Sie es erneut.", voice='Woman', language='de-DE')
            resp.redirect('/process_speech')
    else:
        # resp.play('https://demo.twilio.com/docs/classic.mp3')

        resp.say('You said: {}'.format(speech_result), voice='Woman', language='de-DE')
        resp.redirect('/process_speech')
    return str(resp)

# @sockets.route('/media')
# def echo(ws):
#     app.logger.info("Connection accepted")
#     # A lot of messages will be sent rapidly. We'll stop showing after the first one.
#     has_seen_media = False
#     message_count = 0
#     while not ws.closed:
#         message = ws.receive()
#         if message is None:
#             app.logger.info("No message received...")
#             continue

#         # Messages are a JSON encoded string
#         data = json.loads(message)

#         # Using the event type you can determine what type of message you are receiving
#         if data['event'] == "connected":
#             app.logger.info("Connected Message received: {}".format(message))
#         if data['event'] == "start":
#             app.logger.info("Start Message received: {}".format(message))
#         if data['event'] == "media":
#             if not has_seen_media:
#                 app.logger.info("Media message: {}".format(message))
#                 payload = data['media']['payload']
#                 app.logger.info("Payload is: {}".format(payload))
#                 chunk = base64.b64decode(payload)
#                 app.logger.info("That's {} bytes".format(len(chunk)))
#                 app.logger.info("Additional media messages from WebSocket are being suppressed....")
#                 has_seen_media = True
#         if data['event'] == "closed":
#             app.logger.info("Closed Message received: {}".format(message))
#             break
#         message_count += 1

#     app.logger.info("Connection closed. Received a total of {} messages".format(message_count))


if __name__ == '__main__':
    # app.logger.setLevel(logging.DEBUG)
    # from gevent import pywsgi
    # from geventwebsocket.handler import WebSocketHandler

    # server = pywsgi.WSGIServer(('', HTTP_SERVER_PORT), app, handler_class=WebSocketHandler)
    # print("Server listening on: http://localhost:" + str(HTTP_SERVER_PORT))
    # server.serve_forever()
    app.run(debug=True)
