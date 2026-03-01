# Broadcast Chat – Real-Time Group Chat with FastAPI & WebSockets

A simple, real-time **broadcast-style chat application** where every message sent by any user is instantly visible to **all connected clients** (no private messaging or rooms — pure public broadcast).

Built with:
- **FastAPI** (modern, fast, async Python web framework)
- **WebSockets** (native FastAPI support)
- Plain HTML (no frontend framework — keeps it lightweight)

Perfect as a learning project, WebSocket demo, or starting point for group chat features.

## Features

- Real-time message broadcasting to all connected users
- Simple browser-based chat UI (no login required)
- System messages (welcome, connect/disconnect notifications)
- Timestamp on messages
- Automatic reconnection handling (browser native)
- Interactive WebSocket testing at `/docs`
- Clean async architecture with `ConnectionManager`

## Tech Stack

- Backend: FastAPI + Uvicorn
- Real-time: WebSockets (via FastAPI)
- Frontend: HTML
- Python: 3.8+

## Quick Start

1. Clone the repository

```bash
git clone https://github.com/Chandrakant6/chat_app.git
cd chat_app```

2. Create & activate virtual environment

```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate```

3. Install dependencies

```pip install fastapi uvicorn[standard] websockets```

4. Run the server

```uvicorn main:app --reload --port 8000```

5. Open in browser

```http://localhost:8000/```

Open the same URL in multiple tabs/windows → start chatting!


6. Project Structure
```chat_app/
├── main.py          # FastAPI app + WebSocket logic + embedded HTML client
├── README.md
└── requirements.txt   (you can generate with: pip freeze > requirements.txt)```
