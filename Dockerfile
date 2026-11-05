FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --prefix=/install -r requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY tasks.py ./
RUN python -m compileall -q app scripts tasks.py

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=3000 \
    DATABASE_URL=sqlite:///data/devops_market.db

WORKDIR /app
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p data \
    && chown appuser:appuser data

COPY --from=builder /install /usr/local
COPY --from=builder --chown=appuser:appuser /app /app

USER appuser
VOLUME /app/data
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/api/health', timeout=2)" || exit 1

CMD ["sh", "-c", "python tasks.py db-seed && exec python -m app.core.server"]
