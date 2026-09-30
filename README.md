# fast-api-backend
---------------------------------------------------------
Phase 1: Create a Hello World server with FastApi server
---------------------------------------------------------
Step 1: Install FastAPI and an ASGI Server
i-> pip install fastapi uvicorn
ii-> Create main.py
iii-> uvicorn main:app --reload
iv-> test it. http://127.0.0.1:8000

---------------------------------------------------------
Phase 2: Dockerise the  FastApi server
---------------------------------------------------------
Step 1: Create the Dockerfile with no extension
Now project directory look like this
my-fastapi-app/
├── Dockerfile
├── .dockerignore
├── main.py
└── requirements.txt

Step 2: Build the Docker Image run command docker build -t fastapi-hello-world .

docker build -> Builds an image from a Dockerfile.
-t fastapi-hello-world -> Tags (names) your image so you can reference it easily.
. -> Tells Docker to look for the Dockerfile in the current folder.

Step 3: Run the Docker Container
    i-> run ->  docker run -d -p 8000:8000 --name my-fastapi-container fastapi-hello-world
    ii-> Test it on  http://localhost:8000

-> -d (detached mode): Runs the container in the background so your terminal stays free.
-> -p 8000:8000 (port mapping): Connects host_port:container_port. Traffic sent to your computer's port 8000 is forwarded into port 8000 inside the container.
-> -name my-fastapi-container: Gives your running container a friendly name.
-> fastapi-hello-world: The image you built in Step 4.

Useful Commands to Manage It:
i-> View running containers:	docker ps
ii-> View application logs	docker: logs my-fastapi-container
iii-> Stop the container:	docker stop my-fastapi-container
iv-> Remove the container:	docker rm my-fastapi-container

---------------------------------------------------------
Phase 3: VsCode FastApi Debugger & Docker Debugger
---------------------------------------------------------

i-> Create a .vscode folder and a file launch.json into it.
ii-> For FastApi debugger , Add a break point in main.py and start debugger ad trigger break point by opening http://127.0.0.1:8000 in browser.
iii-> For docker debugger add debugpy in requirements.txt to include it.
    -> Update your Dockerfile so it exposes port 5678 (for the debugger) in addition to port 8000 (for web traffic)
    -> Attach config to launch.json
    -> Build the updated image by running: docker build -t fastapi-debug .
    -> Run the container, mapping both ports: docker run -p 8000:8000 -p 5678:5678 -v "$(pwd):/app" --name fastapi-debug-app --rm fastapi-debug
    -> Attach and Hit a Breakpoint and same as for Fast Api Debugger

-------------------------------------------------------------------------------
Phase 4: Implement ollama provider with enterprises structure and post chat api
-------------------------------------------------------------------------------

    fast-api-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── chat.py
│   ├── services/
│   │   └── llm/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── ollama_provider.py
│   │       ├── openai_provider.py      <-- (Plug-and-play future provider)
│   │       └── factory.py
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           └── chat.py
├── .env
├── Dockerfile
└── requirements.txt

i-> pip install ollama pydantic-settings
ii-> Configure Environment Settings, Create/update:  app/core/config.py
iii-> Define Request & Response Schemas, Create app/schemas/chat.py to validate input and output JSON.
iv-> Create the LLM Interface & Ollama Service,
    * app/services/llm/base.py (The blueprint):
    * app/services/llm/ollama_provider.py (The implementation):
    * app/services/llm/factory.py (The provider resolver):
v-> Create the API Endpoint, Create app/api/v1/chat.py to expose the HTTP route, also Mount this router in app/main.py
vi-> Test it by running your server either from terminal(uvicorn app.main:app --reload --port 8000) or from docker(docker run -p 8000:8000 \
  -e OLLAMA_HOST="http://host.docker.internal:11434" \
  fastapi-debug)


Now Current Architecture Overview:
[Browser / Swagger / Client]
             │
             ▼ (Port 8000)
    [FastAPI Router: /api/v1/chat/ask]
             │
             ▼ (Validates via Pydantic Schema)
       [ChatRequest]
             │
             ▼ (Dependency Injection)
      [LLM Factory] ───► Resolves [OllamaProvider]
                                   │
                                   ▼ (Port 11434 via host.docker.internal)
                           [Ollama Engine on Mac GPU]
                                   │
                                   ▼
                            [llama3.2:1b]