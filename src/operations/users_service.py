from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from encrypt import encrypt_file_content
from fastapi import Depends, HTTPException, UploadFile
from typing import Literal
from utils import get_hash_password
from fastapi.concurrency import run_in_threadpool
from functools import wraps


def get_user_by_id(user_id: int, db: Session):
    
    user: models.Users | None = db.query(models.Users).filter(models.Users.id == user_id).first()

    return user
 

def get_user_by_email(email: str, db: Session):
    
    user: models.Users | None = db.query(models.Users).filter(models.Users.email == email).first()

    return user


async def create_user(user: schemas.UserCreate, db: Session):

    # hash the raw password for security
    user.password = get_hash_password(user.password)

    new_user: models.Users = models.Users(**user.dict(exclude={'confirm_password'}))

    #insert into database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user




async def upload_user_document(
        db: Session, 
        user_id: int, 
        document: UploadFile, 
        document_type: str, 
        **kwargs
         
) -> (models.Marksheets | models.Documents):

    #read the content from the document/file. 
    document_content: bytes = await document.read() 

    # Encrypt the content using Cryptographic library to store sensitive data
    encrypted_document_content: bytes = encrypt_file_content(document_content)

    #fetch the user details to store them in database
    user: models.Users = db.query(models.Users).filter(models.Users.id == user_id).first()
    username: str = user.username
    
    file_name = f'{username}_{document_type}.pdf' #filename to store in database attribute file_name

    if 'application_id' in kwargs:

        new_document: models.Marksheets = models.Marksheets(
            student_id = user_id, application_id = kwargs['application_id'],
            encrypted_marksheet_data = encrypted_document_content,
            file_name = f"{username}_{kwargs['file_name_prefix']}_{document_type}.pdf"

        )

    else:
        new_document: models.Documents = models.Documents(
            student_id = user_id, 
            file_name = file_name, 
            encrypted_data = encrypted_document_content,
            document_type = document_type
        )
    
    
    #Add this into database

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document



async def get_user_document(
        student_id: int, 
        document_type: Literal['passbook', 'marsksheet'],
        db: Session, 
):

    document: models.Documents | None = db.query(models.Documents) \
                                .filter(models.Documents.student_id == student_id, 
                                        models.Documents.document_type == document_type)\
                                .first()

                                           
    return document





async def add_into_profile(
        student_id: int, 
        info: (schemas.PersonalInfo | schemas.ParentInfo | schemas.CollegeInfo),
        profile_type: Literal['personal', 'parental', 'college'],
        db: Session

) -> (models.PersonalInfo | 
      models.ParentInfo | 
      models.CollegeInfo
      ):
    
    #creating a dictionary that maps different database table(class) 
    # for inserting data into appropriate table.

    profiles: dict = {
        'personal': models.PersonalInfo,
        'parental': models.ParentInfo,
        'college': models.CollegeInfo
        }
    
    profile: models.PersonalInfo | models.ParentInfo | models.CollegeInfo = profiles[profile_type]
    
    new_profile = profile(student_id = student_id, **info.dict()) 
    # In the above line it create an instance of db table object 
    # with the help of profile_type, the profile[profile_type] maps the 
    # expected model class for inserting data. 
    
    db.add(new_profile) # Inserting a data to corresponded table
    db.commit()
    db.refresh(new_profile)

    return new_profile



def profile_required(func):
    """
        This function query the database with the student_id,
        used to check whether the student filled all the details such as 
        Personal, Parental and College.

        If not it raises an HTTPException with the status code 400 Bad Request.
    
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):

        db: Session  = kwargs.get('db')
        student_id: int = kwargs.get('user').id

        if not (db and student_id):
            raise HTTPException(
                status_code = 400,
                detail = f'The db or student_id is missing'
            )

        profile =  await run_in_threadpool(
            # db is SqlAlchemy Session object, it basically runs in a Synchrnonus mode, 
            # so it blocking the event loop, we dont want thet, so we use 
            # FastAPIs run_in_threadpool object which actually run this database operation 
            # in separate thread which doesn't block the event loop, 
            # so the event loop allows the other coroutine to rull concurrently.  

            lambda : db.query(models.PersonalInfo, models.ParentInfo, models.CollegeInfo)\
                .select_from(models.PersonalInfo)\
                .join(models.ParentInfo, models.PersonalInfo.student_id == models.ParentInfo.student_id)\
                .join(models.CollegeInfo, models.PersonalInfo.student_id == models.CollegeInfo.student_id)\
                .filter(models.PersonalInfo.student_id == student_id)\
                .first()
            )
        
        if not profile:
            raise HTTPException(
                status_code = 400,
                detail = "Profile incomplete. Please complete your profile before applying for a scholarship."
            )
        
        # If profile is completed, this start executing the main function.
        return await func(*args, **kwargs) 
    
    return wrapper







