from langchain_google_vertexai import ChatVertexAI
import logging
import os
from dotenv import load_dotenv

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Load ENV (only for local) ---
load_dotenv()

# --- GCP Config ---
# 🟢 FIX: Check your custom variable, but fallback to Google's native project ID variable
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")

if not GCP_PROJECT_ID:
    # 🟢 FIX: Log a clear warning instead of throwing a ValueError that crashes the container boot
    logging.warning("⚠️ GCP_PROJECT_ID is not set in the environment yet. It must be provided before calling the LLM.")
else:
    logging.info(f"✅ Using Project: {GCP_PROJECT_ID}")

logging.info(f"✅ Using Location: {GOOGLE_LOCATION}")


# --- Chat Model ---
def get_chat_model(**overrides):
    # 🟢 Double check value at runtime when the function is actually called
    project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if not project_id:
        raise ValueError("❌ Cannot initialize ChatVertexAI: GCP_PROJECT_ID environment variable is missing.")

    config = {
        "model": "gemini-2.5-flash",
        "temperature": 0.0,
        "project": project_id,
        "location": GOOGLE_LOCATION,
    }
    config.update(overrides)

    return ChatVertexAI(**config)