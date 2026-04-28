# Builder
FROM python:3.11.6-slim-bullseye AS builder

ARG POETRY_VERSION=1.8.1
ENV POETRY_VERSION=${POETRY_VERSION}

# Install build deps (kept minimal) and curl for potential network installs
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency manifests first to leverage layer cache when code changes
COPY pyproject.toml poetry.lock /app/

# Install Poetry and export locked requirements to a requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir "poetry==${POETRY_VERSION}" \
    && poetry export --no-interaction --format=requirements.txt --without-hashes --output=requirements.txt

# Create a virtual environment and install dependencies there
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application sources
COPY . /app

# Byte-compile python files to slightly speed startup
RUN /opt/venv/bin/python -m compileall -q /app

# Runtime
FROM python:3.11.6-slim-bookworm AS runtime

# Ensure we don't run as root inside container
RUN groupadd -g 1000 app && useradd -r -u 1000 -g app -m -d /home/app app

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy venv and application from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

# Fix permissions and reduce attack surface
RUN mkdir -p /app/uploads \
    && chown -R app:app /app /opt/venv /app/uploads \
    && chmod -R go-rwx /opt/venv \
    && chmod 750 /app/uploads

# Switch to non-root user
USER app

# Expose port used by Uvicorn
EXPOSE 8000

# Healthcheck using UDS would be better; keep simple TCP check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect((\"127.0.0.1\",8000))" || exit 1

# Default command - run uvicorn with the app
CMD ["uvicorn", "app_backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
