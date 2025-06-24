# Use the official Astral Python image with uv support
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_SYSTEM_PYTHON=1

# Copy all application files (needed for package build)
COPY . .

# Install dependencies using uv (production only)
RUN uv sync --no-dev

# Create necessary directories if they don't exist
RUN mkdir -p assets templates static config_templates

# Expose the port
EXPOSE 5001

# Use gunicorn for production deployment
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5001", "run:app"] 