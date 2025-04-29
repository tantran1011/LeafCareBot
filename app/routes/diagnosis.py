import os
import google.generativeai as genai
from app.config import get_db
from app.utils.image_upload import img2cloud
from fastapi import APIRouter, UploadFile, File, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.inferences import predict_plant_disease
from app.models.database import ChatHistory, User
from app.models.user import ChatResponse
from dotenv import load_dotenv
from app.core.logger import chat_logger 

load_dotenv()
genai.configure(api_key=os.getenv("CHATBOT_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

router = APIRouter()


def format_prompt(user_prompt):
    return f"""
You are a helpful Plant Pathologist assistant AI. (Answer by Vietnamese)

If the following input is a question related to **leaf disease**, respond strictly in this format:
    disease_name: name of disease,
    Reasons: The reasons or factors that lead to the disease,
    Recommendation: How to treat or fix it ?

If the input is the healthy plant without disease, respond like this:
    Status: Good 
    Leaf type: Name of leaf
    Review: Your opinion and the method to keep the leaf is always good  

User input: {user_prompt}
"""


@router.post('/diagnosis_plant', response_model=ChatResponse)
def diagnosis_plant(request: Request, file: UploadFile = File(), db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if not user_id: 
        raise HTTPException(status_code=401, detail="User not login")
    
    secure_url = img2cloud(file, user_id)
    print(secure_url)
    diagnosis = predict_plant_disease(secure_url)
    print(diagnosis)
    response = model.generate_content(format_prompt(diagnosis))
    reply = response.text

    chat_record = ChatHistory(user_id=user_id, question=diagnosis, image_url=secure_url ,response=reply)
    db.add(chat_record)
    db.commit()
    db.refresh(chat_record)
    chat_logger.info("Got response")
    return ChatResponse(response=reply)


@router.get('/plant_information')
def plant_information(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if user:
        history = db.query(ChatHistory).filter(ChatHistory.user_id == id).order_by(ChatHistory.id.desc()).first()
        if not history:
            return {"User": user.username,"Message": "Nothing recorded"}
        return {"Image": history.image_url, "Diagnosis" : history.question}
    raise HTTPException(status_code=401, detail="User not found")


    


    

    
