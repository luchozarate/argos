from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    # El alias captura 'full_name' del formulario y lo mapea a 'name' en Python
    name: str = Field(..., alias="full_name")  
    email: EmailStr
    password: str

    class Config:
        populate_by_name = True
        from_attributes = True