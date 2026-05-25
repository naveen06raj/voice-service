FROM python:3.11-slim

# ============================================
# WORK DIRECTORY
# ============================================

WORKDIR /app

# ============================================
# ENV VARIABLES
# ============================================

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ============================================
# INSTALL SYSTEM PACKAGES
# ============================================

RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# COPY REQUIREMENTS
# ============================================

COPY requirements.txt .

# ============================================
# INSTALL PYTHON PACKAGES
# ============================================

RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# COPY PROJECT
# ============================================

COPY . .

# ============================================
# CLOUD RUN PORT
# ============================================

EXPOSE 8080

# ============================================
# START FASTAPI
# ============================================

# Do NOT hardcode --port 8000 or --host 127.0.0.1
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-3000}"]