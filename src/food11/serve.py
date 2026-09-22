import os
import io

import mlflow
import torch
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from torchvision import transforms


app = FastAPI()


CLASSES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

model = mlflow.pyfunc.load_model(
    "models:/food11@champion"
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()

    image = Image.open(
        io.BytesIO(contents)
    ).convert("RGB")

    image_tensor = transform(image).unsqueeze(0)

    outputs = model.predict(
        image_tensor.numpy()
    )

    logits = torch.tensor(outputs)

    probabilities = torch.softmax(
        logits,
        dim=1,
    )

    confidence, predicted_index = torch.max(
        probabilities,
        dim=1,
    )

    predicted_class = CLASSES[
        predicted_index.item()
    ]

    return {
        "category": predicted_class,
        "confidence": confidence.item(),
    }