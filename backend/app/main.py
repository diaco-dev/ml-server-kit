from fastapi import FastAPI
from app.routers import models
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="MLOps Platform - MVP")

app.include_router(models.router)
Instrumentator().instrument(app).expose(app)

@app.get("/")
async def root():
    return {"message": "MLOps Platform MVP is running!"}