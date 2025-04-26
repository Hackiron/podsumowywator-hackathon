from src.tools.read_through_cache import ReadThroughCache
from fastapi import FastAPI, HTTPException, Request
from src.agent import OrchestratorAgent
from src.dtos import SummaryRequest
from dotenv import load_dotenv
from loguru import logger
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.memory import MessageMemory

load_dotenv()
app = FastAPI(title="Podsumowywator Hackathon Bbackend API")

cache = ReadThroughCache()

orchestrator_agent = OrchestratorAgent(cache)

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
        logger.info(f"Saving thread {request.thread_id} messages")
        MessageMemory.store_thread(request.thread_id, request.messages)

        result = await orchestrator_agent.get_summary(request, cache)
        logger.info("Successfully generated summary")
        return result
    except Exception as e:
        logger.error(f"Error processing summary request: {str(e)}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache")
async def get_cache():
    try:
        logger.info("Fetching cache data")
        cache_data = cache.get_cache()
        logger.info("Successfully fetched cache data")
        return cache_data
    except Exception as e:
        logger.error(f"Error fetching cache data: {str(e)}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/cache")
async def clear_cache():
    try:
        cache.clear()
        logger.info("Cache cleared successfully")
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
