from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit
import random
import string

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}

def generate_room_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

@app.route("/")
def index():
    return """
    <h2>Create or Join Room</h2>
    <button onclick="createRoom()">Create Room</button>
    <input id="code" placeholder="Room Code">
    <button onclick="joinRoom()">Join Room</button>

    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <script>
        const socket = io();

        function createRoom() {
            socket.emit("create_room");
        }

        function joinRoom() {
            const code = document.getElementById("code").value;
            socket.emit("join_room", code);
        }

        socket.on("room_created", (code) => {
            alert("Room created: " + code);
        });

        socket.on("room_joined", (msg) => {
            alert(msg);
        });

        socket.on("error", (msg) => {
            alert(msg);
        });
    </script>
    """

@socketio.on("create_room")
def create_room():
    code = generate_room_code()
    rooms[code] = []
    rooms[code].append(request.sid)
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
    emit("room_joined", "You joined the room", to=code)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
