from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str  # El formulario envía 'username', lo mapeamos aquí

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True