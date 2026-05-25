from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from app.services.stt.whisper_realtime import transcribe_chunk
from app.services.llm.defect_extractor import generate_defect_autofill

router = APIRouter()


@router.websocket("/ws/voice")
async def voice_ws(ws: WebSocket):
    await ws.accept()

    print("🎤 Voice client connected")

    token = None
    property_id = 1

    try:
        while True:

            message = await ws.receive()

            # ============================================
            # RECEIVE TOKEN + PROPERTY_ID
            # ============================================

            if message.get("text"):

                try:
                    data = json.loads(message["text"])

                    token = data.get("token")
                    property_id = data.get("property_id", 1)

                    print("✅ Session initialized")

                    await ws.send_text(json.dumps({
                        "message": "Voice session initialized"
                    }))

                    continue

                except Exception:
                    pass

            # ============================================
            # RECEIVE AUDIO BYTES
            # ============================================

            if message.get("bytes"):

                audio_bytes = message["bytes"]

                print(f"📦 Received audio chunk: {len(audio_bytes)} bytes")

                # ----------------------------------------
                # Voice -> Text
                # ----------------------------------------

                transcript = transcribe_chunk(audio_bytes)

                print("🧠 TRANSCRIPT:", transcript)

                if not transcript:
                    continue

                # ----------------------------------------
                # Validate token
                # ----------------------------------------

                if not token:

                    await ws.send_text(json.dumps({
                        "error": "Token not provided"
                    }))

                    continue

                # ----------------------------------------
                # Text -> Defect Autofill
                # ----------------------------------------

                autofill_result = await generate_defect_autofill(
                    user_text=transcript,
                    token=token,
                    property_id=property_id
                )

                print("✅ AUTOFILL RESULT:", autofill_result)

                # ----------------------------------------
                # Send Final JSON
                # ----------------------------------------

                await ws.send_text(json.dumps({
                    "transcript": transcript,
                    "data": autofill_result
                }))

    except WebSocketDisconnect:

        print("❌ Voice client disconnected")

    except Exception as e:

        print("🔥 WebSocket error:", e)

        try:
            await ws.send_text(json.dumps({
                "error": str(e)
            }))
        except:
            pass