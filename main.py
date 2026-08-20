import os
import time
import threading
import requests
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import db, ensure_indexes
from routes.auth_routes import router as auth_router
from routes.job_routes import router as job_router


# ==========================================
# 1. Background Keep-Alive Bot (Threading)
# ==========================================
def keep_alive_bot():
    """Background thread to keep the Render instance awake by self-pinging."""
    target_url = os.getenv("SELF_PING_URL", "https://applypulse.onrender.com/api/health")
    interval = int(os.getenv("SELF_PING_INTERVAL_SECONDS", "600"))  # Ping every 10 minutes

    print(f"🤖 Keep-Alive Bot initialized! Target: {target_url}")
    time.sleep(20)  # Initial wait server complete boot hone ke liye

    while True:
        try:
            res = requests.get(target_url, timeout=10)
            print(f"⏰ [Keep-Alive Ping Success] Status Code: {res.status_code}")
        except Exception as e:
            print(f"⚠️ [Keep-Alive Ping Failed]: {e}")
        
        time.sleep(interval)

# Background thread ko startup par hi execute kar do
threading.Thread(target=keep_alive_bot, daemon=True).start()


# ==========================================
# 2. WebSocket Connection Manager
# ==========================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


ws_manager = ConnectionManager()


# ==========================================
# 3. Application Lifespan
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    await ensure_indexes()
    yield
    # Shutdown tasks


# ==========================================
# 4. FastAPI Setup & Routes
# ==========================================
app = FastAPI(
    title="ApplyPulse API",
    description="Job Application Tracker API",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.websocket("/ws/jobs")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        ws_manager.disconnect(websocket)


# Include Routers
app.include_router(auth_router)
app.include_router(job_router)


@app.get("/", include_in_schema=False)
async def serve_dashboard():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"app": "ApplyPulse", "docs": "/docs", "health": "/api/health"}


@app.get("/auth/google/callback", include_in_schema=False)
async def serve_google_callback():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"detail": "Dashboard not found"}


@app.get("/api/health")
async def health_check():
    try:
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected ({str(e)})"

    return {
        "status": "ok",
        "app": "ApplyPulse",
        "database": db_status,
        "active_ws_connections": len(ws_manager.active_connections),
    }
