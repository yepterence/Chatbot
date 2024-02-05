# app.py

from sanic import Sanic, Request, Websocket
from sanic.response import json as jsonify
from sanic.log import logger
import websockets
from chatbot import get_chatbot_response, HardCodedChatbot, TorchChatbot
from config import load_config

app = Sanic(__name__)
app.config.from_object(load_config())

# Use the HardCodedChatbot by default
chatbot = HardCodedChatbot()


class ChatRoom:
    def __init__(self):
        self.clients = set()

    async def join(self, ws):
        self.clients.add(ws)

    async def leave(self, ws):
        self.clients.remove(ws)

    async def broadcast(self, sender, message):
        for client in self.clients:
            if client != sender:
                try:
                    await client.send(message)
                except websockets.ConnectionClosed as e:
                    logger.error(f"ConnectionClosed: {e}")


chat_room = ChatRoom()


@app.route("/")
async def hello_world(request):
    return jsonify({"hello": "world"})


@app.websocket("/ws")
async def chat(request: Request, ws: Websocket):
    await chat_room.join(ws)

    try:
        while True:
            message = await ws.recv()
            chatbot_response = await get_chatbot_response(message, chatbot)
            await chat_room.broadcast(ws, f"User #{id(ws)}: {message}")
            await chat_room.broadcast(ws, f"{chatbot_response}")
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"ConnectionClosed: {e}")
    finally:
        await chat_room.leave(ws)


if __name__ == "__main__":
    app.run(host=app.config.HOST, port=app.config.PORT, protocol="websocket")
