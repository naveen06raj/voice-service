from faster_whisper import WhisperModel
import tempfile
import os
import logging

# Global model holder for lazy-loading pattern
_model_instance = None


def get_whisper_model():
    """
    Lazy-loads the Whisper model the exact split second the first audio file lands, 
    rather than blocking the web server during global application module imports.
    """
    global _model_instance
    if _model_instance is None:
        logging.info("⏳ Initializing Whisper Model ('medium'). This may take a moment...")
        _model_instance = WhisperModel(
            "medium",
            device="cpu",          # Keep as CPU for Cloud Run
            compute_type="int8"
        )
        logging.info("✅ Whisper realtime model loaded successfully!")
    return _model_instance


# =====================================================
# TRANSCRIBE AUDIO CHUNK
# =====================================================

def transcribe_chunk(audio_bytes: bytes) -> str:
    """
    Convert browser/mobile audio bytes into text.

    Supported:
    - webm
    - wav
    - mp3

    Requirements:
    - frontend sends full audio blob
    - ffmpeg installed inside the container system environment
    """

    tmp_path = None

    try:
        # =====================================================
        # VALIDATE AUDIO
        # =====================================================
        if not audio_bytes or len(audio_bytes) < 2000:
            print("⚠️ Audio too small")
            return ""

        # =====================================================
        # SAVE TEMP AUDIO FILE
        # =====================================================
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        # =====================================================
        # TRANSCRIBE (Lazy-loaded Model Initialization)
        # =====================================================
        # 🟢 FIX: We fetch the model here, so Uvicorn can open port 3000 first!
        whisper_model = get_whisper_model()

        segments, info = whisper_model.transcribe(
            tmp_path,
            beam_size=5,
            vad_filter=True,
            task="transcribe",
            language=None,
            condition_on_previous_text=False,
            temperature=0.0,
        )

        text_parts = []
        for seg in segments:
            if seg.text:
                text_parts.append(seg.text.strip())

        final_text = " ".join(text_parts).strip()
        print("🧠 TRANSCRIPT:", final_text)

        return final_text

    except Exception as e:
        print("🔥 Whisper transcription error:", e)
        return ""

    finally:
        # =====================================================
        # CLEANUP TEMP FILE
        # =====================================================
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass