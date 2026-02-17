# Use an official Python slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 
    PYTHONUNBUFFERED=1 
    POETRY_VERSION=1.7.1 
    POETRY_HOME="/opt/poetry" 
    POETRY_VIRTUALENVS_CREATE=false 
    POETRY_NO_INTERACTION=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends 
    curl 
    build-essential 
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --only main

# Copy the rest of the application
COPY src/ ./src/
COPY config.yaml README.md ./

# Install the project itself
RUN poetry install --only main

# Set entrypoint
ENTRYPOINT ["python", "-m", "digital_alfred.main"]
