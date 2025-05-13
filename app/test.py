import google.generativeai as genai
from utils.utils import STATE_PROMPT
from dotenv import load_dotenv
import os
from services.weather import get_weather

load_dotenv()

# Thay thế YOUR_API_KEY bằng khóa API thực tế của bạn
genai.configure(api_key=os.getenv('CHATBOT_API_KEY'))

# Chọn một mô hình Gemini
model = genai.GenerativeModel('gemini-2.0-flash')

# Hàm để xử lý một lượt trò chuyện và duy trì state
def chat_with_state(history=[]):

    STATE_PROMPT
    # print("\n--- Bắt đầu trò chuyện ---")

    # Nếu không có lịch sử, tạo một phiên trò chuyện mới
    if not history:
        chat = model.start_chat()
    else:
        chat = model.start_chat(history=history)

    while True:
        user_input = input("Bạn:" )
        if user_input.lower() == 'thoát':
            break

        response = chat.send_message(user_input)
        print("Gemini:", response.text )

        # Cập nhật lịch sử trò chuyện
        history = chat.history

    # print("--- Kết thúc trò chuyện ---")
    return history

def diagnosis(mess, history=[]):
    if not history:
        chat = model.start_chat()
    else:
        chat = model.start_chat(history=history)

    response = chat.send_message(mess)
    print(response.text)
    history = chat.history
    return history

if __name__ == "__main__":
    import cv2
    import onnxruntime as ort
    from utils.class_name import MODEL_PATH, CLASS, normalize_class_name
    import numpy as np

    session = ort.InferenceSession(MODEL_PATH)

    img = cv2.imread("test1.jpg")
    img = cv2.resize(img, (224,224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.expand_dims(img, axis=0)
    img = img.astype(np.float32)

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: img})
    pred_class = np.argmax(outputs)

    disease = normalize_class_name(CLASS[pred_class])
    print(f"Bệnh dự đoán: {disease}")

    conversation_history = []

    # Gửi thông tin bệnh để model nhận xét ban đầu và hỏi thêm
    initial_prompt = f"The detected disease is {disease}. Please give a short initial assessment and then ask for the location, area (in hectares), and the number of plants."
    conversation_history = diagnosis(initial_prompt, conversation_history)

    # Giả định người dùng cung cấp thông tin (trong thực tế bạn cần thu thập từ người dùng)
    location = "Hanoi"
    area = 2
    number = 1500

    # Gửi thông tin người dùng và yêu cầu tính toán năng suất
    user_response_location = {"role": "user", "content": f"The location is {location}."}
    conversation_history = diagnosis(user_response_location["content"], conversation_history)

    user_response_area = {"role": "user", "content": f"The area is {area} hectares."}
    conversation_history = diagnosis(user_response_area["content"], conversation_history)

    user_response_number = {"role": "user", "content": f"The number of plants is {number}."}
    conversation_history = diagnosis(user_response_number["content"], conversation_history)

    weather = get_weather(location)
    final_prompt = f"Now, using the disease '{disease}', location '{location}' (weather: {weather}), area '{area}' hectares, and '{number}' plants, please calculate the Productivity (unit) and explain briefly."
    conversation_history = diagnosis(final_prompt, conversation_history)

    print("\nLịch sử trò chuyện cuối cùng:", conversation_history)