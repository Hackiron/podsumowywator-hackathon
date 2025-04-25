from fastapi import FastAPI, HTTPException
from src.agent import SummaryAgent
from src.dtos import SummaryRequest
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="Podsumowywator Hackathon Bbackend API")

summary_agent = SummaryAgent()

@app.get("/")
async def root():
    return {"message": "Welcome to the Podsumowywator Hackathon Bbackend API"}

@app.post("/ruchniecie")
async def summarize(request: SummaryRequest):
    try:
        result = await summary_agent.get_summary(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
