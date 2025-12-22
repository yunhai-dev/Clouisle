from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.exceptions import DoesNotExist

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, User as UserSchema
from app.schemas.response import Response, success

router = APIRouter()


@router.post("/login/access-token", response_model=Response[Token])
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user = await User.get(username=form_data.username)
    except DoesNotExist:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
    return success(data=token_data, msg="Login successful")


@router.post("/register", response_model=Response[UserSchema])
async def register(
    *,
    user_in: UserCreate,
) -> Any:
    """
    Register a new user (open registration).
    The first registered user will be automatically promoted to Super Admin.
    """
    from app.models.user import Role
    from app.core.init_data import SUPER_ADMIN_ROLE
    
    # Check if username exists
    existing_user = await User.filter(username=user_in.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered",
        )
    
    # Check if email exists
    existing_email = await User.filter(email=user_in.email).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    
    # Check if this is the first user
    user_count = await User.all().count()
    is_first_user = user_count == 0
    
    # Create user
    hashed_password = security.get_password_hash(user_in.password)
    user = await User.create(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=is_first_user,  # First user is superuser
    )
    
    # If first user, assign Super Admin role
    if is_first_user:
        super_admin_role = await Role.filter(name=SUPER_ADMIN_ROLE).first()
        if super_admin_role:
            await user.roles.add(super_admin_role)
        
        # Reload user with roles
        user = await User.get(id=user.id).prefetch_related("roles__permissions")
        return success(data=user, msg="Registration successful. You are the first user and have been promoted to Super Admin!")
    
    return success(data=user, msg="Registration successful")
