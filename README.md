# 🌿 LeafCareBot - AI-powered Plant Diagnosis and Chatbot

A FastAPI backend service that helps users diagnose plant diseases from images and provides gardening advice through an AI chatbot.

[Live API on Render](https://leafcarebot.onrender.com)

---

## 🚀 Features

- 🌱 **Plant Diagnosis**: Upload a leaf image and detect potential diseases using AI models.
- 💬 **AI Chatbot**: Chat with an AI assistant for plant care tips.
- 🔒 **Authentication**: Register and login system with JWT token security.
- 🗄️ **Database**: PostgreSQL integration using SQLAlchemy and Alembic for migrations.
- 🌐 **Deployment**: Hosted on Render (free tier).

---

## ⚙️ Technologies Used

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT Authentication
- TensorFlow / PyTorch (for AI models)
- Uvicorn (ASGI Server)

---

## 🛠️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/tantran1011/LeafCareBot.git
cd LeafCareBot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3.Set up environment variables (Optional)

Create a .env file for secret keys, database URLs, etc. (if needed).

### 4. Run the app locally

```bash
uvicorn main:app --reload
```
The API will be available at: http://127.0.0.1:8000

## 📚 API Endpoints

| Method | Endpoint                  | Description                                                      |
|--------|---------------------------|------------------------------------------------------------------|
| POST   | /auth/register             | Register a new user                                             |
| POST   | /auth/login                | Login and receive JWT token                                     |
| POST   | /chat/chatbot              | Send a message to the AI chatbot                                |
| POST   | /diagnosis/diagnosis_plant | Upload a plant image for disease prediction                      |

You can test the endpoints using Postman or directly through the Swagger UI: 👉 [Swagger UI](http://127.0.0.1:8000)

## 🎨 Frontend (Optional)

Basic index.html is available inside the static/ folder.
In production, the root endpoint / will serve this page.

## ✨ Future Improvements

- Add detailed disease care guides based on diagnosis results.
- Improve chatbot's understanding with fine-tuned models.
- Create a full frontend UI for better user experience.

## 📬 Contact
- Name: Trần Đức Tân
- GitHub: @tantran1011
- LinkedIn: https://www.linkedin.com/in/tan-tran-duc-40bba7307/







