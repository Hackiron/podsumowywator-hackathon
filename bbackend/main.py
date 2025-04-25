from fastapi import FastAPI

app = FastAPI(title="Podsumowywator Hackathon Bbackend API")

@app.get("/")
async def root():
    return {"message": "Welcome to the Podsumowywator Hackathon Bbackend API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 