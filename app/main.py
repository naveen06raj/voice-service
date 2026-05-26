from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

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
        "status": "running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


if __name__ == "__main__":
    # 🌟 Captures the port variable Cloud Run passes (defaulting to 3000)
    port = int(os.environ.get("PORT", 3000)) 
    
    # 🟢 FIXED: Pass the 'app' instance directly instead of a fragile folder string layout path.
    # This completely eliminates "ModuleNotFoundError" or "ImportError" loops at startup.
    uvicorn.run(app, host="0.0.0.0", port=port)