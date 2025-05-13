import os
import time
import google.generativeai as genai
from app.config import get_db
from app.utils.image_upload import img2cloud
from fastapi import APIRouter, UploadFile, File, Request, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.services.inferences import predict_plant_disease
from app.models.database import ChatHistory, User
from app.models.user import ChatResponse, Productivity
from dotenv import load_dotenv
from app.services.weather import get_weather
from google.ai.generativelanguage_v1beta.types import content as genai_content

load_dotenv()
genai.configure(api_key=os.getenv("CHATBOT_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

router = APIRouter()

def start_prompt(disease):
    initial_prompt = f"The detected disease is {disease}. Please give a short initial assessment and then ask for the location, area (in hectares), and the number of plants."
    return initial_prompt


def chat_state(mess, history=[]):
    if not history:
        chat = model.start_chat()
    else:
        chat = model.start_chat(history=history)

    response = chat.send_message(mess)
    history = chat.history
    return history, response


@router.post('/diagnosis_plant', response_model=ChatResponse)
def diagnosis_plant(request: Request, file: UploadFile = File(), db: Session = Depends(get_db)):
    start_total = time.time()

    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not login")

    # 1. Upload cloud
    t1 = time.time()
    secure_url = img2cloud(file, user_id)
    print("✅ Upload URL:", secure_url)
    print("⏱️ Upload time:", round(time.time() - t1, 3), "s")

    # 2. Predict 
    t2 = time.time()
    disease = predict_plant_disease(secure_url)
    print("✅ Diagnosis:", disease)
    print("⏱️ Predict time:", round(time.time() - t2, 3), "s")

    # 3. GeminiAPI
    conversation_history = []
    t3 = time.time()
    initial_prompt = start_prompt(disease)
    conversation_history, response = chat_state(initial_prompt, conversation_history)
    reply = response.text
    print("⏱️ Gemini time:", round(time.time() - t3, 3), "s")

    # 4. storage DB
    t4 = time.time()
    chat_record = ChatHistory(user_id=user_id, question=disease, image_url=secure_url, response=reply)
    db.add(chat_record)
    db.commit()
    print("⏱️ DB commit time:", round(time.time() - t4, 3), "s")

    print("🔥 Total time:", round(time.time() - start_total, 3), "s")

    return ChatResponse(response=reply)


@router.post('/continue_diagnosis', response_model=ChatResponse)
def continue_diagnosis(request: Request, user_response: str = Body(..., embed=True), db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not login")
    
    previous_chats = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.timestamp).all()
    history = []
    for chat in previous_chats:
        user_content = genai_content.Content(
            role="user", 
            parts=[genai_content.Part(text=chat.question)]
            )
        model_content = genai_content.Content(
            role="model", 
            parts=[genai_content.Part(text=chat.response)]
            )
        history.append(user_content)
        history.append(model_content)

    _, response = chat_state(user_response, list(history))

    reply = response.text

    chat_record = ChatHistory(user_id=user_id, question=user_response, response=reply)
    db.add(chat_record)
    db.commit()

    return ChatResponse(response=reply)


@router.post('/calculate_productivity', response_model= ChatResponse)
def calculate_productivity(request: Request, case: Productivity, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not login")
    
    previous_chats = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.timestamp).all()
    history = []
    for chat in previous_chats:
        # print(f"Question: {chat.question}, Type: {type(chat.question)}")
        # print(f"Response: {chat.response}, Type: {type(chat.response)}")
        user_content = genai_content.Content(
            role="user",
            parts=[genai_content.Part(text=chat.question)]
        )
        model_content = genai_content.Content(
            role="model",
            parts=[genai_content.Part(text=chat.response)]
        )
        history.append(user_content)
        history.append(model_content)

    weather = get_weather(case.location)
    print(case.location, case.area, case.num_plants)

    final_prompt = f"Based on the disease, location '{case.location}' (weather: {weather}), area '{case.area}' hectares, and '{case.num_plants}' plants, please calculate the Productivity (unit) and explain briefly."

    _, response = chat_state(final_prompt, list(history))
    reply = response.text
    print(reply)

    chat_record = ChatHistory(user_id=user_id, question=final_prompt, response=reply)
    db.add(chat_record)
    db.commit()

    return ChatResponse(response=reply)


# @router.get('/plant_information')
# def plant_information(id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == id).first()
#     if user:
#         history = db.query(ChatHistory).filter(ChatHistory.user_id == id).order_by(ChatHistory.id.desc()).first()
#         if not history:
#             return {"User": user.username,"Message": "Nothing recorded"}
#         return {"Image": history.image_url, "Diagnosis" : history.question}
#     raise HTTPException(status_code=401, detail="User not found")