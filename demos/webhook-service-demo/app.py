from flask import Flask, Response, jsonify, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/webhook", methods=["POST"])
def respond() -> Response:
    data = request.json
    print(data)
    socketio.emit("data", data)
    return jsonify(data)


if __name__ == "__main__":
    socketio.run(app, host="localhost", port=5000)
