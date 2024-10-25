import io
from typing import Literal
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from exception import EntityNotFoundError
from oauth2 import get_current_admin
import models, schemas
from operations.admin_services import get_application, get_student_overview
from encrypt import decrypt_file_content
from operations.users_service import get_user_by_id





router = APIRouter(
    prefix = '/admin',
    tags = ['Admin'] 
)



@router.get('/student_info/overview/{student_id}')
async def get_student_detail_overview(
    student_id: int,
    db: Session = Depends(get_db),
    admin: schemas.TokenData = Depends(get_current_admin)
):

    student: models.Users | None = get_user_by_id(student_id, db)

    if not student:
        raise EntityNotFoundError(
            message = f'No student found with this id: {student_id}'
        )
    # need to add first student is exist or not with this id
    student_data_overview: tuple | None = await get_student_overview(student_id, db)

    if not student_data_overview:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'Student is not filled all the required details'
        )   
       
    # print(result) 
    # # The result value is actually a tuple, 
    # but fastapi convert it into JSON/dict object for us, thats amazing!
    return student_data_overview



@router.post('/student_verify', status_code = status.HTTP_201_CREATED)
def make_verified_student(
    student: schemas.StudentVerifySchema,
    db: Session = Depends(get_db),
    admin: schemas.TokenData = Depends(get_current_admin) 
                     
):
    """
        This endpoint is used to verify the student, so that they can 
        apply for a scholarship, This enpoint needs a Admin credentials, 
        these endpoint can be used after verifying the student details 
        such as Personal, Parental and College Information provided by the student in this portal,
        In addition they can upload the documents like Passbook, Marksheets etc

        Admin can only make a student verified after verifying these details.
    """  
    existed_student: models.Users | None = get_user_by_id(student.student_id, db)

    if not existed_student:
        raise EntityNotFoundError(
            message = f'No student found with this id: {student.student_id}'
        )
    
    existed_student.is_profile_completed = True

    db.commit()

    return {'message': 'User is verified'}

@router.get('/view_all_applications')
def view_all_application(
    db: Session = Depends(get_db),
    admin: schemas.TokenData = Depends(get_current_admin)
):

    "It returns all the applications submitted by the students"
    
    applications =  get_application(db)

    if not applications:
        raise EntityNotFoundError(
            message = "No applications submitted"
        )
    
    # # The application  is actually a tuple, 
    # but fastapi convert it into JSON/dict object for us, thats amazing!
    return applications


@router.get('/view_particular_application/{application_id}')
def get_particular_application(
    application_id: int, db: Session = Depends(get_db),
    admin: schemas.TokenData = Depends(get_current_admin)
    
):

    application: tuple | None = get_application(db, application_id)

    if not application:
        raise EntityNotFoundError(
            message = f'No Application found with the ID : {application_id}'
        )

    return application


@router.get('/view_scholarship_uploads/')
async def get_scholarship_uploads(
    application_id: int,
    which: Literal['previous', 'latest'] = 'previous',
    db: Session = Depends(get_db),
    admin: schemas.TokenData = Depends(get_current_admin)
):
    marksheet: models.Marsksheets | None = db.query(models.Marsksheets).filter(
        models.Marsksheets.application_id == application_id, models.Marsksheets.file_name.ilike(f'%{which}%')
    ).first()

    if not marksheet:
        raise EntityNotFoundError(
            message = 'No uploads found'
        )

    file_name: str = marksheet.file_name    
    decrypted_markheet: bytes = decrypt_file_content(marksheet.encrypted_marksheet_data)

    pdf_stream = io.BytesIO(decrypted_markheet) 
    
    return StreamingResponse(
        content = pdf_stream,
        status_code = 200,
        media_type = 'application/pdf',
        headers= {
            'Content-Disposition': f'inline; filename={file_name}'
        }
    )
