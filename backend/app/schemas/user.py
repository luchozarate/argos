from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str  # El "usuario" (se guardará en la columna 'name')
    email: EmailStr     # El "mail" (se guardará en la columna 'email')
    password: str  # La "pass" (se guardará en la columna 'password')

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True