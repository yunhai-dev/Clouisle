"""
验证码服务 - 简单数学验证码实现
"""
import random
import secrets
from typing import Optional, Tuple

from app.core.redis import get_redis

# 验证码 key 前缀
CAPTCHA_PREFIX = "captcha:"
CAPTCHA_TTL = 300  # 5 分钟过期


async def generate_captcha() -> Tuple[str, str, str]:
    """
    生成数学验证码
    
    Returns:
        Tuple[captcha_id, question, answer]: 验证码ID、题目、答案
    """
    # 生成唯一 ID
    captcha_id = secrets.token_urlsafe(16)
    
    # 生成数学题
    operators = ['+', '-', '×']
    op = random.choice(operators)
    
    if op == '+':
        a = random.randint(1, 50)
        b = random.randint(1, 50)
        answer = str(a + b)
        question = f"{a} + {b} = ?"
    elif op == '-':
        a = random.randint(10, 99)
        b = random.randint(1, a)  # 确保结果为正
        answer = str(a - b)
        question = f"{a} - {b} = ?"
    else:  # 乘法
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        answer = str(a * b)
        question = f"{a} × {b} = ?"
    
    # 存储到 Redis
    r = await get_redis()
    key = f"{CAPTCHA_PREFIX}{captcha_id}"
    await r.setex(key, CAPTCHA_TTL, answer)
    
    return captcha_id, question, answer


async def verify_captcha(captcha_id: str, user_answer: str) -> bool:
    """
    验证验证码
    
    Args:
        captcha_id: 验证码 ID
        user_answer: 用户输入的答案
        
    Returns:
        True 如果验证通过
    """
    if not captcha_id or not user_answer:
        return False
    
    r = await get_redis()
    key = f"{CAPTCHA_PREFIX}{captcha_id}"
    
    # 获取并删除（一次性使用）
    stored_answer = await r.get(key)
    await r.delete(key)
    
    if stored_answer is None:
        return False
    
    # 比较答案（去除空格）
    return user_answer.strip() == stored_answer.strip()


async def get_captcha_answer(captcha_id: str) -> Optional[str]:
    """
    获取验证码答案（仅用于调试）
    """
    r = await get_redis()
    key = f"{CAPTCHA_PREFIX}{captcha_id}"
    return await r.get(key)
