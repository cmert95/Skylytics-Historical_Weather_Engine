FROM python:3.12-slim

ENV POETRY_VERSION=2.1.3
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get purge -y curl && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/app"

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
COPY src ./src
COPY config ./config

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root

RUN mkdir -p logs data

CMD ["python", "src/main.py"]
