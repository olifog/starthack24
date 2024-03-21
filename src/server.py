import base64
import json
import logging

from flask import Flask
from flask_sockets import Sockets
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)
sockets = Sockets(app)

HTTP_SERVER_PORT = 8000

@app.route("/incoming_call", methods=['POST'])
def incoming_call():
    print('hi')
    resp = VoiceResponse()
    start = resp.start()
    # websocket_url = "wss://https://d12a-194-209-94-52.ngrok-free.app/media"
    # start.stream(url=websocket_url)
    
    gather = Gather(input='speech', action='/process_speech', method='POST', timeout=10)
    gather.say("Hallo, Sie sprechen mit dem Kanton St. Gallen", language="de-DE")
    resp.append(gather)

    resp.redirect('/incoming_call')

    return str(resp)

@app.route("/process_speech", methods=['POST'])
def process_speech():
    print(request)

@app.route("/")
def hello():
    return "Hello World!"

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
    app.logger.setLevel(logging.DEBUG)
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('', HTTP_SERVER_PORT), app, handler_class=WebSocketHandler)
    print("Server listening on: http://localhost:" + str(HTTP_SERVER_PORT))
    server.serve_forever()
