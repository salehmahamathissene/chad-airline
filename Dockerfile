FROM python:3.12-slim

WORKDIR /app

# Faster, cleaner logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# CLI as entrypoint (professional)
ENTRYPOINT ["python", "-m", "cli"]

# Default action: run demo pipeline inside container
CMD ["run", "--out", "/app/out_demo/demo_001", "--run-id", "demo_001", "--flights", "10", "--tickets-per-flight", "5", "--strict"]
