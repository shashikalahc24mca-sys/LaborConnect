from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from . import firebase_client  # noqa: F401  # ensure initialization on import
from .routes_workers import router as workers_router


app = FastAPI(
    title="LaborConnect API",
    description=(
        "Backend for the LaborConnect mobile app. "
        "Provides worker listing, profile management and a simple rule-based "
        "recommendation endpoint that behaves like a basic ML recommender."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RuntimeError)
def firebase_config_error_handler(request: Request, exc: RuntimeError) -> JSONResponse:
    """Return 503 with clear message when Firebase credentials are invalid (e.g. wrong file)."""
    msg = str(exc)
    if "Invalid Firebase credentials" in msg or "Service Account" in msg:
        return JSONResponse(
            status_code=503,
            content={"detail": msg},
        )
    raise exc


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(workers_router)


# Note: run with `uvicorn backend.main:app --reload --port 8010`
