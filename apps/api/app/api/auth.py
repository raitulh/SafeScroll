from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import RefreshSession, User
from app.db.session import get_session
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.security import AuthError, create_access_token, create_refresh_token, decode_token, hash_password, now_utc, token_hash, verify_password
from datetime import timedelta
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer(auto_error=False)

async def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), session: AsyncSession = Depends(get_session)) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    try:
        payload = decode_token(credentials.credentials, "access")
        user_id = int(payload["sub"])
    except (AuthError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.") from exc
    user = await session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive or missing.")
    return user

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    email = payload.email.lower().strip()
    existing = await session.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    try:
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    user = User(email=email, display_name=payload.display_name, password_hash=password_hash)
    session.add(user)
    await session.flush()
    refresh = create_refresh_token(user.id)
    session.add(RefreshSession(token_hash=token_hash(refresh), user_id=user.id, expires_at=now_utc() + timedelta(days=settings.refresh_token_days)))
    await session.commit()
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=refresh, user=UserResponse.model_validate(user))

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.email == payload.email.lower().strip()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    refresh = create_refresh_token(user.id)
    session.add(RefreshSession(token_hash=token_hash(refresh), user_id=user.id, expires_at=now_utc() + timedelta(days=settings.refresh_token_days)))
    await session.commit()
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=refresh, user=UserResponse.model_validate(user))

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest, session: AsyncSession = Depends(get_session)):
    try:
        decoded = decode_token(payload.refresh_token, "refresh")
        user_id = int(decoded["sub"])
    except (AuthError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token.") from exc
    record = await session.scalar(select(RefreshSession).where(RefreshSession.token_hash == token_hash(payload.refresh_token)))
    if not record or record.revoked_at or record.expires_at <= now_utc() or record.user_id != user_id:
        raise HTTPException(status_code=401, detail="Refresh token is no longer valid.")
    record.revoked_at = now_utc()
    new_refresh = create_refresh_token(user_id)
    session.add(RefreshSession(token_hash=token_hash(new_refresh), user_id=user_id, expires_at=now_utc() + timedelta(days=settings.refresh_token_days)))
    user = await session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive or missing.")
    await session.commit()
    return TokenResponse(access_token=create_access_token(user_id), refresh_token=new_refresh, user=UserResponse.model_validate(user))

@router.post("/logout")
async def logout(payload: RefreshRequest, session: AsyncSession = Depends(get_session)):
    record = await session.scalar(select(RefreshSession).where(RefreshSession.token_hash == token_hash(payload.refresh_token)))
    if record:
        record.revoked_at = now_utc()
        await session.commit()
    return {"logged_out": True}

@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(current_user)):
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_me(display_name: str | None = None, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    if display_name is not None and len(display_name) > 120:
        raise HTTPException(status_code=422, detail="Display name is too long.")
    user.display_name = display_name
    await session.commit()
    return UserResponse.model_validate(user)

@router.delete("/me", status_code=204)
async def delete_me(user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    user.is_active = False
    await session.commit()
    return None
