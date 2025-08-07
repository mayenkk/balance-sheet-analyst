from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    verify_password, 
    create_access_token, 
    get_current_user,
    get_password_hash
)
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.auth import (
    UserCreate, 
    UserLogin, 
    Token, 
    UserResponse,
    UserUpdate
)
from app.services.audit import AuditService

router = APIRouter(prefix="/auth", tags=["authentication"])
audit_service = AuditService()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user - only analysts can register"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Force role to be analyst for new registrations
    if user_data.role and user_data.role != UserRole.ANALYST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only analyst role is allowed for new registrations"
        )
    
    # Create new user as analyst
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=UserRole.ANALYST  # Force analyst role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Assign user to all companies (analyst access)
    from app.models.company import Company
    from app.models.user import user_companies
    
    # Get all companies
    all_companies = db.query(Company).all()
    
    # Create user-company relationships for all companies
    for company in all_companies:
        db.execute(
            user_companies.insert().values(
                user_id=user.id,
                company_id=company.id
            )
        )
    
    db.commit()
    
    # Log the registration
    await audit_service.log_action(
        user_id=user.id,
        action="register",
        resource_type="user",
        resource_id=user.id,
        details={
            "role": "analyst",
            "companies_assigned": len(all_companies),
            "access_level": "full_access"
        },
        db=db
    )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user and return access token"""
    
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # Log the login
    await audit_service.log_action(
        user_id=user.id,
        action="login",
        resource_type="user",
        resource_id=user.id,
        db=db
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    
    # Update allowed fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.email is not None:
        # Check if email is already taken
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    db.commit()
    db.refresh(current_user)
    
    # Log the update
    await audit_service.log_action(
        user_id=current_user.id,
        action="update_profile",
        resource_type="user",
        resource_id=current_user.id,
        db=db
    )
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user"""
    
    # Log the logout
    await audit_service.log_action(
        user_id=current_user.id,
        action="logout",
        resource_type="user",
        resource_id=current_user.id,
        db=db
    )
    
    return {"message": "Successfully logged out"} 