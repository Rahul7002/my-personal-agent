# 1. Base Image: Start with an official lightweight Python image
FROM python:3.12-slim

# 2. Working Directory: Set the working folder inside the container
WORKDIR /app

# 3. Dependencies: Copy requirements first to leverage Docker's cache
COPY requirements.txt .

# 4. Install: Run pip install inside the container
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Code: Copy your main.py file into the container's /app directory
COPY main.py .

# # 6. Port: Document that the container listens on port 8000
# EXPOSE 8000

# # 7. Start: The command to run when the container starts
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# 8000 for FastAPI, 5678 for VS Code Debugger
EXPOSE 8000 5678

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]