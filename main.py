from fastapi import FastAPI

# 1. Initialize the FastAPI app instance
app = FastAPI()

# 2. Define a route for the root URL ("/") using the GET HTTP method
@app.get("/")
def read_root():
    # 3. Return a Python dictionary (FastAPI automatically turns this into JSON)
    return {"message": "Hello World"}