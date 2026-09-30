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
Phase 3: VsCode FastApi Debugger
---------------------------------------------------------