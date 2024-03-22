import websocket

def on_message(ws, message):
    print("Received message:", message)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Connection opened")

def check_websocket_server(url):
    ws = None
    try:
        ws = websocket.WebSocketApp(url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close)

        ws.run_forever()
    except Exception as e:
        print("Exception:", e)
    finally:
        if ws:
            ws.close()

if __name__ == "__main__":
    websocket_server_url = "wss://6522-194-209-94-51.ngrok-free.app/conversation"
    check_websocket_server(websocket_server_url)
