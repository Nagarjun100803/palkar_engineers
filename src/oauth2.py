from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt 
from datetime import datetime, timedelta
from database import get_db
import models
from operations.users_service import get_user_by_id
import schemas
from config import oauth2_credentials
from sqlalchemy.orm import Session



oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

def create_access_token(payload: dict):

    to_encode = payload.copy()
    expire = datetime.utcnow() + timedelta(minutes = oauth2_credentials.access_token_expire_minutes)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, key = oauth2_credentials.secret_key, algorithm = oauth2_credentials.algorithm)

    return encoded_jwt


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> schemas.TokenData:

    crediential_exception = HTTPException(
        status_code = 401, 
        detail = 'Your session expired, Please login again.',
        headers={"WWW-Authenticate": "Bearer"}
    )

    try : 

        payload: dict = jwt.decode(token, key = oauth2_credentials.secret_key, 
                                   algorithms=[oauth2_credentials.algorithm]) 
        user_id: int | None = payload.get('user_id')

        user_role: str | None = payload.get('role')
        
        if not (user_id and user_role):
            raise crediential_exception


        user: models.Users | None = get_user_by_id(user_id, db)

        if not user:
            raise crediential_exception
        
    except JWTError: 
        raise crediential_exception
    
    return schemas.TokenData(id = user_id, role = user_role)
    


def get_current_admin(user: schemas.TokenData = Depends(get_current_user)):

    if user.role != 'admin':
        raise HTTPException(
            status_code = 403,
            detail = 'Admin required, You can not perform this operation'
        )
    
    return user


