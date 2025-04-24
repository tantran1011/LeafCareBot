import cv2
import numpy as np
import onnxruntime as ort 
from app.utils.class_name import MODEL_PATH, CLASS, normalize_class_name


def predict_plant_disease(img):
    session = ort.InferenceSession(MODEL_PATH)

    img = cv2.imread(img)
    img = cv2.resize(img, (224,224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  
    img = np.expand_dims(img, axis=0)
    img = img.astype(np.float32)
    
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: img})
    pred_class = np.argmax(outputs)
    format_name = normalize_class_name(CLASS[pred_class])
    return format_name