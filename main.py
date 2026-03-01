from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
import json
from datetime import datetime

app = FastAPI(title="Broadcast Chat - FastAPI WebSockets")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get():
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Broadcast Chat - FastAPI</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
                #messages { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; background: white; border-radius: 8px; margin-bottom: 10px; }
                form { display: flex; }
                #messageText { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
                button { padding: 10px 20px; margin-left: 10px; background: #0064e0; color: white; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #0052cc; }
                .system { color: #888; font-style: italic; }
                .message { margin: 6px 0; }
            </style>
        </head>
        <body>
            <h2>Broadcast Chat (everyone sees everything)</h2>
            <div id="messages"></div>
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off" placeholder="Type your message..." autofocus />
                <button type="submit">Send</button>
            </form>

            <script>
                const ws = new WebSocket(`ws://${location.host}/ws`);
                const messages = document.getElementById('messages');

                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    const msgDiv = document.createElement('div');
                    msgDiv.className = 'message';

                    if (data.type === 'system') {
                        msgDiv.classList.add('system');
                        msgDiv.textContent = data.content;
                    } else if (data.type === 'message') {
                        const time = new Date(data.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                        msgDiv.innerHTML = `<strong>User:</strong> ${data.content} <small>(${time})</small>`;
                    } else if (data.type === 'error') {
                        msgDiv.style.color = 'red';
                        msgDiv.textContent = `Error: ${data.content}`;
                    }

                    messages.appendChild(msgDiv);
                    messages.scrollTop = messages.scrollHeight;
                };

                ws.onopen = () => {
                    addSystem("Connected to chat!");
                };

                ws.onclose = () => {
                    addSystem("Disconnected from server.");
                };

                function addSystem(text) {
                    const div = document.createElement('div');
                    div.className = 'system';
                    div.textContent = text;
                    messages.appendChild(div);
                    messages.scrollTop = messages.scrollHeight;
                }

                function sendMessage(event) {
                    event.preventDefault();
                    const input = document.getElementById("messageText");
                    const message = input.value.trim();
                    if (message) {
                        ws.send(JSON.stringify({ type: "message", content: message }));
                        input.value = '';
                    }
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    client_id = id(websocket)  # simple unique id, or use uuid later

    try:
        # Welcome (only to this client)
        await manager.send_personal_message(
            json.dumps({"type": "system", "content": "Welcome to Broadcast Chat! Messages are public."}),
            websocket
        )

        while True:
            data_text = await websocket.receive_text()
            try:
                data = json.loads(data_text)
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({"type": "error", "content": "Invalid JSON"}),
                    websocket
                )
                continue

            if data.get("type") == "message":
                content = data.get("content", "").strip()
                if content:
                    broadcast_payload = json.dumps({
                        "type": "message",
                        "content": content,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    await manager.broadcast(broadcast_payload)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(
            json.dumps({"type": "system", "content": f"Someone left the chat (client {client_id})"})
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        manager.disconnect(websocket)
