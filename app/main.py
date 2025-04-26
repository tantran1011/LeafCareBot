from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import auth, chat, diagnosis
import os
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from app.middleware.middleware import log_request_time
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name='static')
app.add_middleware(SessionMiddleware, secret_key = os.getenv("SECRET_KEY"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(log_request_time)

app.include_router(auth.router, prefix='/auth')
app.include_router(chat.router, prefix='/chat')
app.include_router(diagnosis.router, prefix="/diagnosis")

@app.get('/')
def home():
    return {"message": "Server is running"}