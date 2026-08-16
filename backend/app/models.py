from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr
    password: str



class LoginUser(BaseModel):
    email: EmailStr
    password: str



class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str



class ForgotPassword(BaseModel):
    email: EmailStr



class VerifyResetOTP(BaseModel):
    email: EmailStr
    otp: str



class ResetPassword(BaseModel):
    email: EmailStr
    new_password: str