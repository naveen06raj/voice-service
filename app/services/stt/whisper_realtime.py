from faster_whisper import WhisperModel
import tempfile
import os

# =====================================================
# LOAD WHISPER MODEL ONCE
# =====================================================

model = WhisperModel(
    "medium",
    device="cpu",          # change to "cuda" if GPU available
    compute_type="int8"
)

print("✅ Whisper realtime model loaded")


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
    - ffmpeg installed
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
        # TRANSCRIBE
        # =====================================================

        segments, info = model.transcribe(
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