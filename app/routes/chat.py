import google.generativeai as genai
from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.user import ChatRequest, ChatResponse
from app.models.database import ChatHistory, User
from app.config import get_db
from app.core.logger import chat_logger
from sqlalchemy.orm import Session
import os 
from dotenv import load_dotenv 

load_dotenv()
genai.configure(api_key=os.getenv("CHATBOT_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

# pattern = r'"disease_name":\s*"([^"]+)"|' \
#           r'"confidence":\s*([0-9.]+)|' \
#           r'"recommendation":\s*"([^"]+)"'

router = APIRouter()

@router.post('/chatbot', response_model=ChatResponse)
def chat(request: Request, chat_req: ChatRequest, db: Session = Depends(get_db)):
    
    user_id = request.session.get("user_id")

    if not user_id: 
        raise HTTPException(status_code=401, detail="User not login")

    response = model.generate_content(chat_req.message)
    reply = response.text

    chat_record = ChatHistory(user_id=user_id, question=chat_req.message, response=reply)
    db.add(chat_record)
    db.commit()
    db.refresh(chat_record)
    chat_logger.info("Got response")
    return ChatResponse(response=reply)


@router.get("/chat_history")
def chat_history(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if user:
        history = db.query(ChatHistory).filter(ChatHistory.user_id == id).all()
        if not history:
            return {"User": user.username,"Message": "Nothing recorded"}
        return {"User": user.username, "Chat History" : history}
    raise HTTPException(status_code=401, detail="User not found")