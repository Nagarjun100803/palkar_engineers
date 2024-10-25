from typing import List, Literal
from fastapi import APIRouter, File, Query, UploadFile, status, BackgroundTasks, Depends, Form, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import EmailStr
import models, schemas
from database import get_db
from sqlalchemy.orm import Session 
from utils import get_hash_password, create_token_for_reset, verify_token
from exception import EntityNotFoundError
from oauth2 import get_current_user
from mailing import create_and_send_reset_email
from operations.users_service import (
    get_user_by_id, get_user_by_email,
    create_user, add_into_profile)


router = APIRouter(
    prefix ='/users',
    tags = ['Users']
)



@router.get('', response_model = List[schemas.UserOut])
async def get_all_users(db: Session = Depends(get_db)):
    
    users: List[models.Users] = db.query(models.Users).all()
    
    return users



@router.get('/{user_id}', response_model = schemas.UserOut)
async def get_particular_user(
    user_id: int, 
    db: Session = Depends(get_db)
):

    # user: models.Users | None = db.query(models.Users).filter(models.Users.id == user_id).first()
    user: models.Users | None = get_user_by_id(user_id, db)
    
    if not user: 
        raise EntityNotFoundError(
            message = f'No user found with the id : {user_id}'
        )
    
    return user


@router.post('', status_code = status.HTTP_201_CREATED, response_model = schemas.UserOut)
async def Signup(
    user: schemas.UserCreate = Form(...), 
    db: Session = Depends(get_db)
):
    
    if user.password != user.confirm_password: 
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Password and Confirm password is not matching!'
        )

    registered_user: models.Users | None = get_user_by_email(user.email, db)
    
    if registered_user : 
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'The Username or Email already exists, Try with different Email/Username.'
        )

    new_user: models.Users = await create_user(user, db)
    # create_user(user, db)

    return new_user

@router.post('/reset_password_request')
async def request_reset_password(
    background_task: BackgroundTasks, 
    email: EmailStr = Form(...),
    db: Session = Depends(get_db)
):
    
    user: models.User | None = get_user_by_email(email, db)

    if not user:
        raise HTTPException(
            status_code = 404, detail = f'No account found with this email: {email}. You must register to reset password.'
        ) 
    
    token = create_token_for_reset({'user_id': user.id})

    ## Sending an access token to reset the password
    # create_and_send_reset_email(to_addr = email, token = token)
    background_task.add_task(create_and_send_reset_email, to_addr = email, token = token)

    return {
        'message': f'Please check the email {email} to reset the password...'
    }




@router.post('/reset_password')
async def reset_password(
    reset_token: str, 
    new_password: str =  Form(...), 
    db: Session = Depends(get_db)
):
    
    payload: dict | None = verify_token(reset_token)

    if not payload:
        raise HTTPException(
            status_code = status.HTTP_408_REQUEST_TIMEOUT,
            detail = 'Token is expired/Invalid Token. Make a new request to reset password.'
        )
    
    user_id: int = payload.get('user_id')

    hashed_password = get_hash_password(new_password)

    update_user_query = db.query(models.Users).filter(models.Users.id == user_id)

    
    update_user_query.update({'password': hashed_password})
    db.commit()

    return {'message': 'Password reset step is done!'}



@router.post('/profile_setup/personal_info', status_code = status.HTTP_201_CREATED)
async def add_personal_info(
    personal_info: schemas.PersonalInfo = Form(...),
    user: schemas.TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
  
    existed_student_info: models.PersonalInfo = db.query(models.PersonalInfo) \
                                                .filter(models.PersonalInfo.student_id == user.id)\
                                                .first()
    
    if existed_student_info:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Already you filled the personal_info'
        )

    profile: models.PersonalInfo = await add_into_profile(
        user.id, 
        profile_type='personal', 
        info=personal_info, 
        db=db)
    
    return {
        'message': f'{profile.first_name}! your personal info saved😀'
    }

    
@router.post('/profile_setup/parental_info', status_code = status.HTTP_201_CREATED)
async def add_parental_info(
    parental_info: schemas.ParentInfo = Form(...),
    user: schemas.TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    existed_student_info: models.ParentInfo = db.query(models.ParentInfo)\
                                              .filter(models.ParentInfo.student_id == user.id)\
                                              .first()
    if existed_student_info:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Already you filled the personal info!'
        )                          
    
    new_parental_info: models.ParentInfo = await add_into_profile(
        student_id = user.id,
        profile_type = 'parental',
        info = parental_info,
        db = db
    )

    return {
        'message': f'parental info saved successfully'
    }

@router.post('/profile_setup/college_info', status_code = status.HTTP_201_CREATED)
async def add_college_info(
    college_info: schemas.CollegeInfo = Form(...),
    user: schemas.TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    existed_student_info: models.CollegeInfo = db.query(models.CollegeInfo)\
                                              .filter(models.CollegeInfo.student_id == user.id)\
                                              .first()
    if existed_student_info:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Already you filled the college info!'
        )                          
    
    new_college_info: models.CollegeInfo = await add_into_profile(
        student_id = user.id,
        profile_type = 'college',
        info = college_info,
        db = db
    )

    return {
        'College Name': new_college_info.college_name,
        'Branch': new_college_info.branch
    }




