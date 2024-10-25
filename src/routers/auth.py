from fastapi import HTTPException, Depends, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter
from database import get_db
from sqlalchemy.orm import Session
from utils import verify_password
from oauth2 import create_access_token
import schemas, models
from fastapi.security import OAuth2PasswordRequestForm




router = APIRouter(
    tags=['Authentication']
)

@router.post('/login')
async def login_user(db: Session = Depends(get_db), 
                     user_credentials: OAuth2PasswordRequestForm = Depends()) -> schemas.Token:

    user: models.Users = db.query(models.Users).filter(models.Users.email == user_credentials.username).first()

    if not user: 
        raise HTTPException(
            status_code = 404, 
            detail = f"No User found with the email '{user_credentials.username}'..."
        )
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code = 401,
            detail = 'Incorrect Password'
        )

    token = create_access_token({'user_id': user.id, 'role': user.role})
    
    return schemas.Token(access_token = token)


