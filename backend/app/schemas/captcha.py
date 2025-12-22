from pydantic import BaseModel


class CaptchaResponse(BaseModel):
    """验证码响应"""
    captcha_id: str
    question: str


class CaptchaVerifyRequest(BaseModel):
    """验证码验证请求"""
    captcha_id: str
    answer: str
