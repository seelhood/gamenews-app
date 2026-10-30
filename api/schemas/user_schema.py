from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=4, max_length=100)

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str = "user"
    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(user|admin)$")