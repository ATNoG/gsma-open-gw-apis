from flask import Flask, request, Response, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


@app.route("/webhook", methods=["POST"])
def respond():
    data = request.json
    print(data)
    socketio.emit("data", data)
    return jsonify(data)


if __name__ == "__main__":
    socketio.run(app, host="localhost", port=5000)
