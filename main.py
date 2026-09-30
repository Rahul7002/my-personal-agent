from fastapi import FastAPI

# 1. Initialize the FastAPI app instance
app = FastAPI()

# 2. Define a route for the root URL ("/") using the GET HTTP method
@app.get("/")
def read_root():
    greeting = "Hello"
    audience = "World"
    full_message = f"{greeting}, {audience}!"
    return {"message": full_message}