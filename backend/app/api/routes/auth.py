from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.models.organization import Organization
from app.models.user import User
from app.models.datasource import DataSource
from app.schemas.auth import UserRegister, UserLogin, Token, UserOut

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user and automatically creates a new Organization for them.
    Also creates default active DataSources for SAP, Utility, and Travel.
    """
    # Check if user already exists
    stmt_username = select(User).where(User.username == user_in.username)
    res_username = await db.execute(stmt_username)
    if res_username.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists."
        )

    stmt_email = select(User).where(User.email == user_in.email)
    res_email = await db.execute(stmt_email)
    if res_email.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    # Check if organization exists or create new one
    stmt_org = select(Organization).where(Organization.name == user_in.organization_name)
    res_org = await db.execute(stmt_org)
    org = res_org.scalars().first()
    
    if not org:
        org = Organization(name=user_in.organization_name)
        db.add(org)
        await db.flush()  # populate org.id
        
        # Seed default DataSources for this organization
        sap_ds = DataSource(name="SAP CSV Upload", source_type="sap", organization_id=org.id)
        utility_ds = DataSource(name="Utility Portal CSV Upload", source_type="utility", organization_id=org.id)
        travel_ds = DataSource(name="Mock Corporate Travel REST API", source_type="travel", organization_id=org.id)
        db.add_all([sap_ds, utility_ds, travel_ds])
        await db.flush()

    hashed_pw = get_password_hash(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pw,
        organization_id=org.id,
        is_active=True,
        is_analyst=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Standard OAuth2 password flow login yielding JWT tokens.
    """
    stmt = select(User).where(User.username == form_data.username)
    res = await db.execute(stmt)
    user = res.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the authenticated user details.
    """
    return current_user
