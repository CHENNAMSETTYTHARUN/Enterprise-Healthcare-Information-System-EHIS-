from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="admin@ehis.com")
    password: str = Field(..., min_length=6, example="Admin123!")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserMinResponse"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

class UserMinResponse(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    roles: List[str]

TokenResponse.model_rebuild()
