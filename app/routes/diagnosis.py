import os
import time
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

def format_prompt(disease_name):
    return f"""
Bạn là trợ lý AI am hiểu về bệnh lý cây trồng. Trả lời bằng tiếng Việt, đúng theo một trong hai định dạng sau:

Nếu có bệnh:
- disease_name: Tên bệnh
- Reasons: Nguyên nhân
- Recommendation: Cách chữa trị hoặc phòng tránh

Nếu là 'healthy':
- Status: Good
- Leaf type: Loại lá
- Review: Nhận xét & cách giữ cây khỏe

Disease name: {disease_name}
"""


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
    diagnosis = predict_plant_disease(secure_url)
    print("✅ Diagnosis:", diagnosis)
    print("⏱️ Predict time:", round(time.time() - t2, 3), "s")

    # 3. GeminiAPI
    t3 = time.time()
    response = model.generate_content(format_prompt(diagnosis))
    reply = response.text
    print("⏱️ Gemini time:", round(time.time() - t3, 3), "s")

    # 4. storage DB
    t4 = time.time()
    chat_record = ChatHistory(user_id=user_id, question=diagnosis, image_url=secure_url, response=reply)
    db.add(chat_record)
    db.commit()
    print("⏱️ DB commit time:", round(time.time() - t4, 3), "s")

    print("🔥 Total time:", round(time.time() - start_total, 3), "s")

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


    


    

    
