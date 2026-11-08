FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:0.11.24 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src ./src
COPY apps/__init__.py ./apps/__init__.py
COPY apps/api ./apps/api
COPY apps/worker ./apps/worker
RUN useradd --create-home --uid 10001 appuser
ENV PATH="/app/.venv/bin:$PATH"

FROM base AS api
RUN uv sync --frozen --no-dev --extra retrieval
ENV HOME=/home/appuser FASTEMBED_CACHE_PATH=/home/appuser/.cache/fastembed
RUN mkdir -p /data/documents /home/appuser/.cache && chown -R appuser /data /home/appuser/.cache
USER appuser
EXPOSE 8000
CMD ["uvicorn", "apps.api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS ingest
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        fonts-dejavu-core \
        libreoffice-impress \
        libreoffice-writer \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-tur \
    && rm -rf /var/lib/apt/lists/*
RUN uv sync --frozen --no-dev --extra ingest --extra retrieval
ENV DOCLING_ARTIFACTS_PATH=/opt/docling-models HOME=/home/appuser FASTEMBED_CACHE_PATH=/home/appuser/.cache/fastembed
RUN python -c "from rapidocr import RapidOCR; RapidOCR()" \
    && chmod -R a+rX /app/.venv
RUN mkdir -p /data/documents /opt/docling-models /home/appuser/.cache/huggingface /home/appuser/.cache/fastembed \
    && chown -R appuser /data /opt/docling-models /home/appuser/.cache
USER appuser
CMD ["python", "-m", "apps.worker.main"]
