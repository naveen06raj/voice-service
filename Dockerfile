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
# 🟢 FIXED: Changed from 8080 to match your Cloud Build yaml port target configuration!
EXPOSE 3000

# ============================================
# START FASTAPI
# ============================================
# 🟢 FIXED: Instead of fragile raw string uvicorn commands, execute your clean main.py 
# script file entrypoint directly. This guarantees your port environment variables map correctly.
CMD ["python", "app/main.py"]