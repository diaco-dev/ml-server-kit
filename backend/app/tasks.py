# backend/app/tasks.py
from app.celery_app import celery_app
import subprocess
import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.crud import update_model_status
import uuid

engine = create_async_engine(os.getenv("DATABASE_URL"))


@celery_app.task(bind=True, max_retries=3)
def deploy_model_task(self, model_id: str):
    async def _update(status: str, endpoint: str = None):
        async with AsyncSession(engine) as db:
            await update_model_status(db, model_id, status, endpoint)

    try:
        # find directory
        result = subprocess.run(
            "find /app/models-storage -name model.* | head -1",
            shell=True, capture_output=True, text=True
        )
        if not result.stdout:
            raise Exception("Model file not found")

        model_file_path = result.stdout.strip()
        model_dir = os.path.dirname(model_file_path)
        container_name = f"model-{model_id[:8]}"

        # remove docker container
        subprocess.run(f"docker stop {container_name} || true", shell=True)
        subprocess.run(f"docker rm {container_name} || true", shell=True)

        # run new container
        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "-v", f"{model_dir}:/model:ro",
            "-v", "/app/model-template/serve.py:/model/serve.py",
            "python:3.11-slim",
            "bash", "-c",
            "pip install fastapi uvicorn scikit-learn torch tensorflow onnx onnxruntime && "
            "uvicorn serve:app --host 0.0.0.0 --port 8000"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Docker run failed: {result.stderr}")

        # get port
        port_result = subprocess.run(
            f"docker port {container_name} 8000/tcp",
            shell=True, capture_output=True, text=True
        )
        port = port_result.stdout.strip().split(":")[-1]
        endpoint = f"http://host.docker.internal:{port}/predict"

        asyncio.run(_update("ready", endpoint))
        print(f"Model deployed: {endpoint}")

    except Exception as exc:
        asyncio.run(_update("failed"))
        raise self.retry(exc=exc)