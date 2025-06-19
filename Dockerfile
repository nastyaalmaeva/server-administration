FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .[test]

COPY src/ ./src/
COPY tests/ ./tests/

EXPOSE 8114

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8114", "--reload"]
