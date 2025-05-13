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
    response: str

class Productivity(BaseModel):
    location: str
    area: int
    num_plants: int 