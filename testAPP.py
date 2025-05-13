from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', logger=True, engineio_logger=True)

def test_background_task():
    while True:
        print("Test background task running...")
        socketio.sleep(1)

@app.route('/')
def index():
    return "Hello, Flask-SocketIO!"

if __name__ == '__main__':
    print("Starting minimal Flask-SocketIO app...")
    socketio.start_background_task(test_background_task)
    socketio.run(app, debug=False)