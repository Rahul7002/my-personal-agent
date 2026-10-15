# 1. Base Image: Start with an official lightweight Python image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# 2. Working Directory: Set the working folder inside the container
WORKDIR /app

# 2.1. Install system dependencies (curl is useful for container health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Dependencies: Copy requirements first to leverage Docker's cache
COPY requirements.txt .

# 4. Install: Run pip install inside the container
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Code: Copy your main.py file into the container's /app directory
COPY . .

# 8. Create a non-root user and grant permissions
RUN useradd -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# # 6. Port: Document that the container listens on port 8000
# EXPOSE 8000

# # 7. Start: The command to run when the container starts
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# 8000 for FastAPI, 5678 for VS Code Debugger
EXPOSE 8000 5678
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]