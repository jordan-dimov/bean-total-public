from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from src.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from src.auth_schema import Token
from src.database import engine, get_db
from src.models import Base, User

app = FastAPI(
    title="BeanTotal Accounting Automation Platform",
    description="An online platform for automating business processes at accounting firms.",
    version="0.0.1",
)


@app.on_event("startup")
async def startup():
    # On startup, ensure that all database tables exist
    Base.metadata.drop_all(bind=engine)
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session=Depends(get_db),  # noqa: B008
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
async def root(current_user: Annotated[User, Depends(get_current_active_user)]):
    return {"message": f"Hello {current_user.email}"}
