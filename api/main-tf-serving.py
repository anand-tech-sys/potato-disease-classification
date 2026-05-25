from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
import requests

app = FastAPI()

# CORS (Optional)
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TensorFlow Serving Endpoint
endpoint = "http://localhost:8501/v1/models/potatoes_model:predict"

# Class Labels
CLASS_NAMES = [
    "Early Blight",
    "Late Blight",
    "Healthy"
]


@app.get("/ping")
async def ping():
    return "Hello, I am alive"


# Image Preprocessing
def read_file_as_image(data) -> np.ndarray:
    image = Image.open(BytesIO(data)).convert("RGB")
    image = image.resize((256, 256))
    image = np.array(image)
    image = image.astype(np.float32)
    return image


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    try:

        # Read image
        image = read_file_as_image(await file.read())

        # Add batch dimension
        img_batch = np.expand_dims(image, 0)

        # Convert image to JSON
        json_data = {
            "instances": img_batch.tolist()
        }

        # Send request to TensorFlow Serving
        response = requests.post(
            endpoint,
            json=json_data
        )

        # Handle errors
        if response.status_code != 200:
            return {
                "error": response.text
            }

        # Extract predictions
        prediction = np.array(
            response.json()["predictions"][0]
        )

        # Get class
        predicted_class = CLASS_NAMES[np.argmax(prediction)]

        # Get confidence
        confidence = float(np.max(prediction))

        return {
            "class": predicted_class,
            "confidence": confidence
        }

    except Exception as e:

        return {
            "error": str(e)
        }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="localhost",
        port=8000
    )