FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y --fix-missing \
    bison \
    build-essential \
    gperf \
    flex \
    libasound2-dev \
    libcups2-dev \
    libdrm-dev \
    libegl1-mesa-dev \
    libnss3-dev \
    libpci-dev \
    libpulse-dev \
    libudev-dev \
    nodejs \
    libxtst-dev \
    gyp \
    ninja-build \
    libglib2.0-0 \
    libgl1-mesa-glx \
    ffmpeg \
    libsm6 \
    libxext6 \
    libnss3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

ENV PORT=8080

# Command to run the application
CMD ["python", "mainGui.py"]
