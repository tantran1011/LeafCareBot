import google.generativeai as genai
from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.user import ChatRequest, ChatResponse
from app.models.database import ChatHistory, User
from app.config import get_db
from app.core.logger import chat_logger
from sqlalchemy.orm import Session
import os
import re 
from dotenv import load_dotenv 

load_dotenv()
genai.configure(api_key=os.getenv("CHATBOT_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

def format_prompt(user_prompt):
    return f"""
    You are a helpful doctor assistant AI. Given a disease-related question, respond strictly in this JSON format:

    {{
      "disease_name": "<name of disease>",
      "confidence": <number from 0 to 1>,
      "recommendation": "<how to treat/fix>"
    }}

    Question: {user_prompt}
    """

pattern = r'"disease_name":\s*"([^"]+)"|' \
          r'"confidence":\s*([0-9.]+)|' \
          r'"recommendation":\s*"([^"]+)"'

router = APIRouter()

@router.post('/chatbot', response_model=ChatResponse)
def chat(request: Request, chat_req: ChatRequest, db: Session = Depends(get_db)):
    
    user_id = request.session.get("user_id")

    if not user_id: 
        raise HTTPException(status_code=401, detail="User not login")

    response = model.generate_content(format_prompt(chat_req.message))
    reply = response.text

    chat_record = ChatHistory(user_id=user_id, question=chat_req.message, response=reply)
    db.add(chat_record)
    db.commit()
    db.refresh(chat_record)
    chat_logger.info("Got response")
    m = re.findall(pattern, reply)
    disease_name, confidence, recommendation = m
    return ChatResponse(disease_name=disease_name[0],
                        confidence=confidence[1],
                        recommendation=recommendation[-1])


@router.get("/chat_history")
def chat_history(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if user:
        history = db.query(ChatHistory).filter(ChatHistory.user_id == id).first()
        if not history:
            return {"User": user.username,"Message": "Nothing recorded"}
        return {"User": user.username, "Chat History" : history}
    raise HTTPException(status_code=401, detail="User not found")