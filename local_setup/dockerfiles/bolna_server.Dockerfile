FROM python:3.10.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    git \
    ffmpeg \
    gcc \
    g++ \
    python3-dev \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel

# Install uvicorn first
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install uvicorn

# Install common dependencies that bolna requires
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install \
    python-dotenv \
    pydantic \
    fastapi \
    huggingface-hub \
    numpy \
    tqdm \
    requests \
    sqlalchemy \
    pymysql \
    bcrypt \
    python-jose[cryptography] \
    email-validator

# Install bolna package with verbose output for debugging
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --verbose git+https://github.com/Oxin-ai/oxin@main || \
    (echo "Failed to install bolna package. See error above." && exit 1)

# Copy application files
COPY local_setup/quickstart_server.py /app/
COPY local_setup/presets /app/presets
# Copy local bolna package to override installed package
COPY bolna /app/bolna

EXPOSE 5001

CMD ["uvicorn", "quickstart_server:app", "--host", "0.0.0.0", "--port", "5001"]
