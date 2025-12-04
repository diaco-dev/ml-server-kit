# MLOps MVP Project

## Setup
1. Clone or create the directory structure.
2. Run `docker-compose up --build -d`

## Test
- API Docs: http://localhost:8000/docs
- Upload model: `curl -F "name=test_model" -F "framework=sklearn" -F "file=@path/to/your_model.pkl" http://localhost:8000/upload`
- List models: `curl http://localhost:8000/models`
- Predict: `curl "http://localhost:8000/predict/test_model?x=5.0"`
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (login: admin/admin)

## Notes
- For production, migrate to Kubernetes and PostgreSQL.