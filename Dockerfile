# Build stage
FROM python:3.12.6-alpine3.20 AS build

WORKDIR /app

COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


COPY ./src /app/src

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

COPY --from=build /opt/venv /opt/venv
COPY --from=build /app/src ./src

# Expose a port 
EXPOSE 5000

# Use the Python virtual environment in the runtime stage
ENV PATH="/opt/venv/bin:$PATH"

ENV OPENWEATHER_API_KEY=''
ENV CITIES=''

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:5000/health || exit 1

WORKDIR /app/src

CMD ["python", "weather_api.py"]
