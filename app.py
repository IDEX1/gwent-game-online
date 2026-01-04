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
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Gwent Online</title>
    <style>
        body {
            font-family: Arial;
            background: #1e1e1e;
            color: white;
            text-align: center;
            margin-top: 80px;
        }
        button, input {
            padding: 10px;
            margin: 5px;
            font-size: 16px;
        }
        #roomCode {
            font-size: 22px;
            margin-top: 20px;
            color: #00ff99;
        }
    </style>
</head>
<body>

    <h1>🃏 Gwent Online</h1>

    <button onclick="createRoom()">Create Room</button>
    <br><br>

    <input id="codeInput" placeholder="Enter Room Code">
    <button onclick="joinRoom()">Join Room</button>

    <div id="roomCode"></div>
    <div id="status"></div>

    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <script>
        const socket = io();

        function createRoom() {
            socket.emit("create_room");
        }

        function joinRoom() {
            const code = document.getElementById("codeInput").value.toUpperCase();
            socket.emit("join_room", code);
        }

        socket.on("room_created", (code) => {
            document.getElementById("roomCode").innerText =
                "Room Code: " + code;
            document.getElementById("status").innerText =
                "Waiting for another player...";
        });

        socket.on("room_joined", (msg) => {
            document.getElementById("status").innerText = msg;
        });

        socket.on("error", (msg) => {
            alert(msg);
        });
    </script>

</body>
</html>
"""


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
