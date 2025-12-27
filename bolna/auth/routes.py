from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from bolna.auth.database import get_db
from bolna.auth.models import User, Tenant
from bolna.auth.schemas import UserSignup, UserLogin, Token, UserResponse
from bolna.auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from datetime import timedelta
from bolna.auth.security import JWT_EXPIRE_MINUTES
import re
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])


def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from tenant name."""
    # Convert to lowercase
    slug = name.lower()
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # If empty after processing, generate a random slug
    if not slug:
        slug = f"tenant-{uuid.uuid4().hex[:8]}"
    return slug


def ensure_unique_slug(db: Session, base_slug: str) -> str:
    """Ensure slug is unique by appending a number if needed."""
    slug = base_slug
    counter = 1
    while db.query(Tenant).filter(Tenant.slug == slug).first() is not None:
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """Create a new tenant and user account."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate unique slug for tenant
    base_slug = generate_slug(user_data.tenant_name)
    tenant_slug = ensure_unique_slug(db, base_slug)
    
    # Create new tenant
    new_tenant = Tenant(
        name=user_data.tenant_name,
        slug=tenant_slug,
        is_active=True
    )
    db.add(new_tenant)
    db.flush()  # Flush to get tenant.id without committing
    
    # Create new user with role "owner"
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        tenant_id=new_tenant.id,
        role="owner",
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token with tenant_id and role
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": new_user.id,
            "email": new_user.email,
            "tenant_id": new_user.tenant_id,
            "role": new_user.role
        },
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token with tenant_id and role
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "tenant_id": user.tenant_id,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")
