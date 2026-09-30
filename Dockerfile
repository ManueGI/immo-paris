# syntax=docker/dockerfile:1

# ---- Build stage: install locked dependencies and the project into /app/.venv ----
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.20 /uv /bin/uv

# Compile bytecode for faster startup; copy files out of the cache mount; use the image's
# Python instead of downloading one
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Dependencies first, in their own layer: code changes do not reinstall them
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project

# Then the project itself, installed as a regular package (not linked to the sources)
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable


# ---- Runtime stage: only the virtual environment and what Alembic needs ----
FROM python:3.12-slim

# Unprivileged user: a compromised process does not get root in the container
RUN groupadd --system app && useradd --system --gid app --no-create-home app

# Files stay owned by root: the app user can read and run them, but not modify them
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
# Migrations run from this image too (alembic upgrade head)
COPY alembic.ini pyproject.toml ./
COPY migrations ./migrations

# /app is read-only for the app user: downloaded DVF files go to a temporary directory
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/tmp/dvf

USER app
EXPOSE 8000

# One process per container: scale by running more containers, not more workers.
# --proxy-headers: trust X-Forwarded-* from the load balancer in front of the API
CMD ["uvicorn", "immo_paris.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
