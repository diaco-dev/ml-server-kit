from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import ModelRegistry
from app.schemas import ModelCreate
import uuid

async def create_model(db: AsyncSession, name: str, framework: str):
    model = ModelRegistry(
        id=uuid.uuid4(),
        name=name,
        version="1.0.0",
        framework=framework,
        status="uploaded"
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return model

async def get_models(db: AsyncSession):
    result = await db.execute(select(ModelRegistry).order_by(ModelRegistry.created_at.desc()))
    return result.scalars().all()

async def get_latest_ready_model(db: AsyncSession, name: str):
    result = await db.execute(
        select(ModelRegistry)
        .where(ModelRegistry.name == name, ModelRegistry.status == "ready")
        .order_by(ModelRegistry.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()

async def update_model_status(db: AsyncSession, model_id: str, status: str, endpoint: str = None):
    await db.execute(
        update(ModelRegistry)
        .where(ModelRegistry.id == model_id)
        .values(status=status, endpoint=endpoint)
    )
    await db.commit()