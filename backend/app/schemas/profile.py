from pydantic import BaseModel

class UserUpdate(BaseModel):
    full_name: str | None = None
    preferred_currency: str | None = None
    timezone: str | None = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
