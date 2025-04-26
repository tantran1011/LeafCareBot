import cv2
import numpy as np
import requests
import onnxruntime as ort 
from app.utils.class_name import MODEL_PATH, CLASS, normalize_class_name


session = ort.InferenceSession(MODEL_PATH)


def predict_plant_disease(img_url):
    response = requests.get(img_url)
    if response.status_code != 200:
        raise ValueError("Failed to fetch image from URL")
    
    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)

    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    img = cv2.resize(img, (224,224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  
    img = np.expand_dims(img, axis=0)
    img = img.astype(np.float32)
    
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: img})
    pred_class = np.argmax(outputs)
    format_name = normalize_class_name(CLASS[pred_class])
    return format_name