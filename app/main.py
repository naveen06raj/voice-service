from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.voice_ws import router as voice_router

app = FastAPI(
    title="Voice Autofill Service",
    description="Realtime voice to text service for autofill",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change to your mobile app domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_router)


@app.get("/")
async def root():
    return {
        "service": "voice-autofill-service",
        "status": "running cloud"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }