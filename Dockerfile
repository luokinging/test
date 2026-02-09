# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    curl && \
    rm -rf /var/lib/apt/lists/*


COPY pyproject.toml uv.lock* /app/

RUN uv pip install --system --no-cache -r pyproject.toml

# Keep build tools for adding new dependencies inside the container (e.g., uv add)
# Removing them reduces ~100-150 MB, but prevents recompilation of packages like mysqlclient
# RUN apt-get purge -y build-essential pkg-config && \
#     apt-get autoremove -y

COPY . /app/

EXPOSE 8000