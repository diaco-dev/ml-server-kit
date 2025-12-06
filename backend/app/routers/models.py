from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.database import get_db
from app.tasks import deploy_model_task
import shutil
import os

router = APIRouter(prefix="/api/v1", tags=["models"])

STORAGE = "/app/models-storage"
os.makedirs(STORAGE, exist_ok=True)


@router.post("/models", response_model=schemas.ModelResponse)
async def upload_model(
        name: str = Form(...),
        framework: str = Form(...),
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db)
):
    model_dir = f"{STORAGE}/{name}/1.0.0"
    os.makedirs(model_dir, exist_ok=True)

    ext = file.filename.split(".")[-1]
    model_path = f"{model_dir}/model.{ext}"
    with open(model_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    model = await crud.create_model(db, name=name, framework=framework)
    deploy_model_task.delay(str(model.id))
    return model


@router.get("/models", response_model=list[schemas.ModelResponse])
async def list_models(db: AsyncSession = Depends(get_db)):
    return await crud.get_models(db)


@router.get("/predict/{model_name}")
async def predict_proxy(model_name: str, x: float = 1.0, db: AsyncSession = Depends(get_db)):
    model = await crud.get_latest_ready_model(db, model_name)
    if not model or not model.endpoint:
        raise HTTPException(404, "Model not ready")
    return {"forwarded_to": model.endpoint, "input": x, "note": "در نسخه کامل اینجا forward می‌شود"}