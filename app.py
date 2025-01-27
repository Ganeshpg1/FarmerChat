from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import openai
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "fallback_secret")
socketio = SocketIO(app)

# Set OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return render_template("chat.html")

@socketio.on("connect")
def handle_connect():
    print("User connected")

@socketio.on("join")
def handle_join(data):
    username = data.get("username")
    print(f"{username} joined the chat")
    emit("user_joined", {"username": username}, broadcast=True)

@socketio.on("send_message")
def handle_message(data):
    username = data["username"]
    message = data["message"]

    # Check for abusive content using OpenAI
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Is this message abusive? '{message}' Respond with Yes or No.",
        max_tokens=5
    )
    abuse_check = response.choices[0].text.strip().lower()

    if abuse_check == "yes":
        emit("message", {"username": "System", "message": "Message blocked due to abusive content."}, to=request.sid)
    else:
        emit("message", {"username": username, "message": message}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
