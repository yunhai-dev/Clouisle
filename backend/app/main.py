from fastapi import FastAPI

app = FastAPI(title="Clouisle API")

@app.get("/")
async def root():
    return {"message": "Welcome to Clouisle API"}
