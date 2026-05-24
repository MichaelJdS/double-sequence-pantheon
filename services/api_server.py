from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import DASHBOARD_DIR
from core.models import ManualSpinRequest


def create_app(state, repository, engine, feed) -> FastAPI:
    app = FastAPI(title="Double Sequence Pantheon", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    dashboard_path = Path(DASHBOARD_DIR)
    dashboard_path.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=dashboard_path), name="static")

    @app.get("/")
    def root():
        return FileResponse(dashboard_path / "index.html")

    @app.get("/api/health")
    def health():
        return {
            "ok": True,
            "strategies": repository.count(),
            "feed": feed.status(),
        }

    @app.get("/api/state")
    def get_state():
        snapshot = state.snapshot()
        snapshot["strategies_count"] = repository.count()
        snapshot["feed"] = feed.status()
        return snapshot

    @app.get("/api/strategies")
    def get_strategies():
        return [strategy.model_dump(mode="json") for strategy in repository.all()]

    @app.post("/api/strategies/reload")
    def reload_strategies():
        total = repository.reload()
        return {
            "ok": True,
            "strategies": total,
        }

    @app.post("/api/spins/manual")
    def add_manual_spin(payload: ManualSpinRequest):
        try:
            return engine.handle_color(color=payload.color, source=payload.source)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post("/api/feed/demo/start")
    def start_demo():
        feed.start()
        return {
            "ok": True,
            "feed": feed.status(),
        }

    @app.post("/api/feed/demo/stop")
    def stop_demo():
        feed.stop()
        return {
            "ok": True,
            "feed": feed.status(),
        }

    return app