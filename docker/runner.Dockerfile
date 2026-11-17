# syntax=docker/dockerfile:1
# The test runner: Playwright's image, which holds Chromium, Firefox and WebKit with their system libraries, plus uv,
# Python 3.14 and this project's packages. The echo service runs from it too.
FROM mcr.microsoft.com/playwright/python:v1.65.2-noble@sha256:38dd67fc654b56b3cba611e4c8eb71cd33750e1cd29eea2a5dc00b484817a75f

COPY --from=ghcr.io/astral-sh/uv:0.12.24@sha256:3af4716e991d6956a41e573eab705d0ee08500cd829ed30293eb8472f372c65a /uv /usr/local/bin/uv
# Keep the venv and Python outside /work, which compose mounts over with the repo.
ENV UV_PYTHON_INSTALL_DIR=/opt/python \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_PREFERENCE=only-managed \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /work
COPY pyproject.toml uv.lock .python-version README.md LICENSE ./
RUN uv sync --locked --no-install-project
COPY src ./src
RUN uv sync --locked
