from fastapi import FastAPI, HTTPException, Request
from src.agent import OrchestratorAgent
from src.dtos import SummaryRequest
from dotenv import load_dotenv
from loguru import logger
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

load_dotenv()
app = FastAPI(title="Podsumowywator Hackathon Bbackend API")

orchestrator_agent = OrchestratorAgent()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Request validation failed: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation Error",
            "errors": exc.errors(),
        },
    )


@app.get("/")
async def root():
    return {"message": "Welcome to the Podsumowywator Hackathon Bbackend API"}


@app.post("/ruchniecie")
async def summarize(request: SummaryRequest):
    try:
        logger.info(f"Received summary request for channel: {request.channel_id}")
        logger.info(f"Number of messages to summarize: {len(request.messages)}")

        result = await orchestrator_agent.get_summary(request)
        logger.info("Successfully generated summary")
        return result
    except Exception as e:
        logger.error(f"Error processing summary request: {str(e)}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
