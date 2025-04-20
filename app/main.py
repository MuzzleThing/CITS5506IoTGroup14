from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'amber_pearl_latte_is_the_best'
socketio = SocketIO(app)

@app.route('/')
def openHomepage():
    return render_template('homepage.html') # TODO: make the actual pages


if __name__ == '__main__': # Run the server by command line: python main.py
    socketio.run(app, debug=True) 
    # Format to specify IP and port: socketio.run(app, host="0.0.0.0", port=5000, debug = True)