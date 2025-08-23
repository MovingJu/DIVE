FROM python:3.10-slim

# Copy uv binary from official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies (no mount syntax, for Railway compatibility)
RUN uv sync --frozen --no-install-project

# Copy rest of the project
COPY . .

# Sync again to install the project itself
RUN uv sync --frozen

# Set Railway port environment variable
ENV PORT=8000

# Expose the port for documentation (not strictly required by Railway)
EXPOSE 8000

# Run the app
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
