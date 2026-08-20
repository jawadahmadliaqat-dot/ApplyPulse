import os
import asyncio
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import httpx

from database import db, ensure_indexes
from routes.auth_routes import router as auth_router
from routes.job_routes import router as job_router

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


async def self_ping_worker() -> None:
    """Keep an active deployment warm when an explicit self-ping URL is configured."""
    ping_url = os.getenv("SELF_PING_URL")
    if not ping_url:
        return

    interval = int(os.getenv("SELF_PING_INTERVAL_SECONDS", "180"))
    async with httpx.AsyncClient(timeout=15.0) as client:
        while True:
            try:
                await client.get(ping_url)
            except httpx.HTTPError:
                pass
            await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    await ensure_indexes()
    ping_task = asyncio.create_task(self_ping_worker())
    try:
        yield
    finally:
        ping_task.cancel()
        await asyncio.gather(ping_task, return_exceptions=True)


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