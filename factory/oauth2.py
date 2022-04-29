from datetime import timedelta, datetime
from jose import JWTError, jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from factory.config import settings
from factory.schema import token_schema
from factory.utils import ManagerType


# the tokenurl is whatever url in auth.py login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_min
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_day


def create_access_token(
    data: token_schema.PayloadDataCreate, expires_delta: timedelta | None = None
) -> str:

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        # this is how you update pydantic model.
    to_encode = data.copy(update={"exp": expire})
    # change back to dict coz encode accepts dict not class.
    encoded_jwt = jwt.encode(to_encode.dict(), SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: token_schema.PayloadDataCreate) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy(update={"exp": expire})
    encoded_refresh_jwt = jwt.encode(to_encode.dict(), SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_jwt


def verify_access_token(
    _token: str, credential_exceptions
) -> None | token_schema.PayloadData:
    try:
        payload = jwt.decode(_token, SECRET_KEY, algorithms=[ALGORITHM])
        manager_id: str = payload.get("manager_id")
        if manager_id is None:
            raise credential_exceptions
        # altho payload has "exp", we only need id, type and, name. that's why i use payloaddata instead of payloadData create.
        token_data = token_schema.PayloadData(**payload)
    except JWTError:
        raise credential_exceptions
    return token_data


def verify_refresh_token(
    _token: str, credential_exceptions
) -> None | token_schema.PayloadData:
    try:
        payload = jwt.decode(_token, SECRET_KEY, algorithms=[ALGORITHM])
        manager_id: str = payload.get("manager_id")
        if manager_id is None:
            raise credential_exceptions
        token_data = token_schema.PayloadData(**payload)
    except JWTError:
        raise credential_exceptions
    return token_data


def renew_token(_token: str):
    refresh_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Token",
    )
    payload_data = verify_refresh_token(_token, refresh_exception)
    return token_schema.TokenCreate(
        access_token=create_access_token(data=payload_data),
        refresh_token=create_refresh_token(data=payload_data),
        token_type="Bearer",
    )


def get_manager(
    _token: str = Depends(oauth2_scheme),
) -> None | token_schema.PayloadData:
    credential_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_access_token(_token, credential_exceptions)


def get_admin(
    current_token: token_schema.PayloadData = Depends(get_manager),
) -> None | token_schema.PayloadData:
    if not ManagerType.is_admin(current_token.manager_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You do not have access."
        )
    return current_token


def get_issuer(
    current_token: token_schema.PayloadData = Depends(get_manager),
) -> None | token_schema.PayloadData:
    if not ManagerType.is_issuer(current_token.manager_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You do not have access."
        )
    return current_token


def get_listener(
    current_token: token_schema.PayloadData = Depends(get_manager),
) -> None | token_schema.PayloadData:
    if not ManagerType.is_listener(current_token.manager_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You do not have access."
        )
    return current_token
