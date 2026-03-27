FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CHROMA_PERSIST_DIRECTORY=/app/data/chroma

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY sql ./sql

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "cfhee_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
