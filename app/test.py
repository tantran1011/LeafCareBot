import google.generativeai as genai
from utils.utils import STATE_PROMPT
from dotenv import load_dotenv
import re
import os

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
        user_input = input("Bạn: ")
        if user_input.lower() == 'thoát':
            break

        response = chat.send_message(user_input)
        print("Gemini:", response.text)

        # Cập nhật lịch sử trò chuyện
        history = chat.history

    # print("--- Kết thúc trò chuyện ---")
    return history

if __name__ == "__main__":
    # Bắt đầu một phiên trò chuyện mới
    conversation_history = chat_with_state()

    # Bạn có thể tiếp tục trò chuyện với cùng lịch sử nếu muốn
    # print("\n--- Tiếp tục trò chuyện (nếu muốn) ---")
    conversation_history = chat_with_state(history=conversation_history)

    # print("\nLịch sử trò chuyện cuối cùng:", conversation_history)
    user_content = []
    model_content = []
    for item in conversation_history:
        txt = re.search(r'text:\s*"([^"]+)"', str(item))
        role = re.search(r'role:\s*"([^"]+)"', str(item))
        if role.group(1) == 'user':
            user_content.append(txt.group(1))
        else:
            model_content.append(txt.group(1))
    print(model_content)

