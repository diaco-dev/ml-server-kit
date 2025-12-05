from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase
import uuid

class Base(DeclarativeBase):
    pass

class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    version = Column(String, default="1.0.0")
    framework = Column(String, nullable=False)
    status = Column(String, default="uploaded")  # uploaded, deploying, ready, failed
    endpoint = Column(String, nullable=True)
    created_at = Column(String, server_default=text("TIMEZONE('utc', now())"))