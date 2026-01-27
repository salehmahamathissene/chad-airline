FROM python:3.12-slim

LABEL org.opencontainers.image.title="Airline Edition — Risk & Revenue Simulation Engine"
LABEL org.opencontainers.image.version="1.0.x"
LABEL org.opencontainers.image.description="Monte Carlo → Risk → Board → Execution → CEO PDF (audit-grade artifacts)"
LABEL org.opencontainers.image.licenses="Proprietary"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Create non-root user + ensure output dir exists
RUN useradd -m appuser \
 && mkdir -p /app/out_demo \
 && chown -R appuser:appuser /app

USER appuser

ENTRYPOINT ["python", "-m", "cli"]
CMD ["run", "--out", "/app/out_demo", "--run-id", "demo_001", "--flights", "10", "--tickets-per-flight", "5", "--strict"]
