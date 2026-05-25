from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf

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

# Load TensorFlow SavedModel
MODEL = tf.keras.models.load_model("../saved_models/1")

CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]


@app.get("/ping")
async def ping():
    return "Hello, I am alive"


# Read and preprocess image
def read_file_as_image(data) -> np.ndarray:

    image = Image.open(BytesIO(data)).convert("RGB")

    # Resize according to model input shape
    image = image.resize((256, 256))

    # Convert to numpy array
    image = np.array(image)

    # Convert uint8 -> float32
    image = image.astype(np.float32)

    # Normalize image
    image = image / 255.0

    return image


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    # Read image
    image = read_file_as_image(await file.read())
    img_batch = np.expand_dims(image, 0)

    # Get SavedModel inference function
    infer = MODEL.signatures["serving_default"]

    # Run prediction
    predictions = infer(
        input_1=tf.constant(img_batch)
    )

    # Extract prediction tensor
    predictions = list(predictions.values())[0].numpy()

    # Get predicted class
    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]

    # Get confidence
    confidence = np.max(predictions[0])

    return {
        "class": predicted_class,
        "confidence": float(confidence)
    }


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)