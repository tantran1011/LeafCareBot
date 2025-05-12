import google.generativeai as genai
from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.user import ChatRequest, ChatResponse
from app.models.database import ChatHistory, User
from app.config import get_db
from app.core.logger import chat_logger
from sqlalchemy.orm import Session
import os 
from dotenv import load_dotenv 
from google.ai.generativelanguage_v1beta.types import content as genai_content


load_dotenv()
genai.configure(api_key=os.getenv("CHATBOT_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

router = APIRouter()

router = APIRouter()

def convert_history_to_gemini_format(history_db: list[ChatHistory]) -> list[genai_content.Content]:
    """
    Converts chat history from the database format to the format expected by the Gemini API.
    """
    history_gemini = []
    for record in history_db:
        if record.question:
            history_gemini.append(
                genai_content.Content(
                    role="user",
                    parts=[genai_content.Part(text=record.question)],
                )
            )
        if record.response:
            history_gemini.append(
                genai_content.Content(
                    role="model",
                    parts=[genai_content.Part(text=record.response)],
                )
            )
    return history_gemini

@router.post('/chatbot', response_model=ChatResponse)
async def chat(request: Request, chat_req: ChatRequest, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not login")

    # Truy xuất lịch sử trò chuyện từ database
    history_db = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.timestamp).all()

    # Chuyển đổi lịch sử sang định dạng Gemini
    history_gemini = convert_history_to_gemini_format(history_db)

    chat = model.start_chat(history=history_gemini)
    response = chat.send_message(chat_req.message)
    reply = response.text

    # Lưu tin nhắn mới vào database
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