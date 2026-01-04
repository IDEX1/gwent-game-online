import eventlet
eventlet.monkey_patch()

import os
import random
import string
from flask import Flask, request
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}

def generate_room_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

@app.route("/")
def index():
    return "Server is running"

@socketio.on("create_room")
def create_room():
    code = generate_room_code()
    rooms[code] = [request.sid]
    join_room(code)
    emit("room_created", code)

@socketio.on("join_room")
def join(code):
    if code not in rooms:
        emit("error", "Room not found")
        return
    if len(rooms[code]) >= 2:
        emit("error", "Room full")
        return

    rooms[code].append(request.sid)
    join_room(code)
    emit("room_joined", "Player joined", to=code)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
