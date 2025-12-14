from fastapi import FastAPI
import os
import pickle
import torch
import numpy as np
import onnxruntime as ort

app = FastAPI()

# upload models
model_file = next(f for f in os.listdir("/model") if f.startswith("model."))
model_path = os.path.join("/model", model_file)

if model_file.endswith(".pkl"):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
elif model_file.endswith(".pt"):
    model = torch.load(model_path)
elif model_file.endswith(".onnx"):
    model = ort.InferenceSession(model_path)
else:
    raise ValueError("Unsupported model format")

@app.get("/predict")
def predict(x: float = 1.0):
    input_data = np.array([[x, x * 2]])
    if "pkl" in model_file:
        pred = model.predict(input_data)[0]
    elif "pt" in model_file:
        pred = model(torch.tensor(input_data)).item()
    elif "onnx" in model_file:
        pred = model.run(None, {"input": input_data.astype(np.float32)})[0]
    return {"prediction": float(pred)}