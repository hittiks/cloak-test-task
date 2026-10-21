FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# CloakBrowser ships its own Chromium, which needs these shared libraries.
# bookworm-slim has none of them; the first missing one is libglib-2.0.so.0. (from playwright logs)
# xvfb is the virtual display for headed mode (HEADLESS=False).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libx11-xcb1 \
    libfontconfig1 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxshmfence1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    libcairo-gobject2 \
    libgdk-pixbuf-2.0-0 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-unifont \
    fonts-freefont-ttf \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    fonts-tlwg-loma-otf \
    fonts-urw-base35 \
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser \
    && useradd -r -g appuser -m -d /home/appuser appuser

WORKDIR /code

ENV HOME=/home/appuser \
    UV_CACHE_DIR=/home/appuser/.cache/uv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG DEPENDENCY_GROUPS

WORKDIR /code

RUN chown appuser:appuser /code

ENV PATH="/code/.venv/bin:$PATH" \
    PYTHONPATH="/code"

COPY --chown=appuser:appuser pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache \
     && chown -R appuser:appuser /code

COPY --chown=appuser:appuser ./app ./app

USER appuser
