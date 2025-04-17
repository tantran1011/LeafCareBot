from pydantic import BaseModel

class Register(BaseModel):
    username: str 
    password: str 

class Login(BaseModel):
    username: str
    password: str 

class UserRespone(BaseModel):
    username: str

class ChatRequest(BaseModel):
    message: str 

class ChatResponse(BaseModel):
    disease_name: str
    confidence: str 
    recommendation: str