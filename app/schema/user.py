from pydantic import BaseModel,EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    user_type: str = "user"

class UserOut(BaseModel):
    username: str
    email: EmailStr
    user_type: str

    class Config:
        orm_mode = True
        
class Token(BaseModel):
    access_token: str
    token_type: str