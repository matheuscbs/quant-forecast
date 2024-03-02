# Use a base image with Python installed. The version should match your project's requirements.
FROM python:3.8-slim

# Set a working directory to avoid using absolute paths
WORKDIR /app

# Define PYTHONPATH to include the /app directory
ENV PYTHONPATH="/app"

# Install Poetry
# Avoid creating a virtual environment inside the Docker container
# because the container itself provides isolation
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

# Copia o pyproject.toml e, opcionalmente, o poetry.lock para /app
COPY pyproject.toml poetry.lock* /app/

# Install dependencies using Poetry
RUN poetry install --no-interaction --no-ansi

# The code will be mounted via Docker Compose, so we do not need to COPY it here

# Keep the container running to allow interactive development
CMD ["sleep", "infinity"]
