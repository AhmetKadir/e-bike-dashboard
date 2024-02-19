FROM python:3.9-slim

RUN apt-get update && apt-get install -y \libglib2.0-0

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

ENV PORT=8080

# Command to run the application
CMD ["python", "mainGui.py"]
