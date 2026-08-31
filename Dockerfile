# syntax=docker/dockerfile:1
#
# Multi-stage build that isolates the dev and prod environments.
#   base -> shared runtime + pinned runtime dependencies
#   dev  -> adds lint/type-check/test tooling and the full source tree
#   prod -> runtime deps + source only, running as a non-root user
#

FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    PATH=/venv/bin:$PATH
WORKDIR /app
RUN python -m venv /venv \
    && /venv/bin/pip install --upgrade pip wheel
COPY requirements.txt ./
RUN /venv/bin/pip install -r requirements.txt


# --- Development image: linting, type checking and tests ---
FROM base AS dev
COPY requirements-dev.txt ./
RUN /venv/bin/pip install -r requirements-dev.txt
COPY . .
CMD ["bash"]


# --- Production image: minimal runtime, non-root ---
FROM base AS prod
COPY models ./models
COPY tracking ./tracking
COPY output ./output
COPY utils ./utils
COPY main.py service.py entrypoint.sh config.example.json ./
RUN chmod +x entrypoint.sh \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app app \
    && chown -R app:app /app
USER app
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--config", "/app/config.json"]
