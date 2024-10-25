from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, condecimal, conint
from typing import Any, Literal, Annotated
import models
from database import get_db
from sqlalchemy.orm import Session
import schemas, oauth2
from operations.users_service import (upload_user_document, profile_required)



router = APIRouter(
    prefix = '/students/scholarship_form',
    tags = ['Scholorhip Form']
)



async def scholarship_form_data( 
        
    current_semester: conint(ge=1, le=8) = Form(...), #type: ignore
    latest_sem_cgpa: condecimal(max_digits = 3, decimal_places = 2, ge = 1, le = 10) = Form(...), #type: ignore
    previous_sem_cgpa: condecimal(max_digits = 3, decimal_places = 2, ge = 1, le = 10)  = Form(...), #type: ignore
    arrears_in_previous_sem: bool = Form(False),
    parental_info: Literal[
        'Both parents are alive',
        'Single Parent',
        'Both are passed away'        
    ] = Form(...),
    any_medical_issue: bool = Form(True) 

) -> schemas.RequestScholarship:
    
    return schemas.RequestScholarship(

        current_semester =  current_semester,
        latest_sem_cgpa = latest_sem_cgpa,
        previous_sem_cgpa = previous_sem_cgpa,
        arrears_in_previous_sem = arrears_in_previous_sem,
        parental_info = parental_info,
        any_medical_issue = any_medical_issue
    
    )


async def create_scholarship(
        scholarship_request: schemas.RequestScholarship, 
        db: Session, 
        user: schemas.TokenData
) -> models.ScholarshipApplications:
    scholarship_application: models.ScholarshipApplications = models.ScholarshipApplications(
                    student_id = user.id, 
                    difference_in_cgpa = (
            #subtrating the values to get difference in CGPA to check any improvement in performance
                    scholarship_request.latest_sem_cgpa - scholarship_request.previous_sem_cgpa),
                    **scholarship_request.dict()
            )

    db.add(scholarship_application)
    db.commit() 
    db.refresh(scholarship_application)

    return scholarship_application


@router.post('/apply', status_code = status.HTTP_201_CREATED)
@profile_required
async def apply_for_scholarship(
    scholarship_request: Annotated[schemas.RequestScholarship, Depends(scholarship_form_data)],
    latest_marksheet: Annotated[UploadFile, File(...)],
    previous_marksheet: Annotated[UploadFile, File(...)],
    db: Session = Depends(get_db),
    user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    
    """ 
        These endpoint allows individual user to apply for a scholarship,
        we have to make sure that every applicant can only apply for 
        the scholarship exactly once per semester.
    """
    accepted_content_type: str = 'application/pdf'

    # Check all the uploded files are pdf. Because we only allow pdf files for now.
    if not all([
            (latest_marksheet.content_type == accepted_content_type), 
            (previous_marksheet.content_type == accepted_content_type)
        ]):

        raise HTTPException(
            status_code = 400,
            detail = 'Please upload pdf files, other files are not accepted'
        )

    # Checking whether the profile is completed or not, We only allow the students 
    # who have completed or uploaded full details of them like personal, parental and college info

    # profile: Any | None = await get_profile(student_id = user.id, db = db)

    # if not profile :
    #     raise HTTPException(
    #         status_code = status.HTTP_403_FORBIDDEN,
    #         detail = 'You must complete your profile to apply for a scholarship.'
    #     )
    
    existed_application: models.ScholarshipApplications = db.query(models.ScholarshipApplications)\
                                .filter(models.ScholarshipApplications.student_id == user.id)\
                                .first()
    
    if existed_application:
        raise HTTPException(
            status_code = 400,
            detail = 'Already applied for a scholarship'
        )

    #Add a new application for the user to the database
    scholarship_application = await create_scholarship(scholarship_request, db, user)

    #uploading the documents
    uploaded_latest_marksheet: models.Marsksheets = await upload_user_document(
        db, user.id, latest_marksheet, 'marksheet',
        application_id =  scholarship_application.id,
        file_name_prefix = 'latest_sem'
    )

    uploaded_previous_marksheet: models.Marsksheets = await upload_user_document(
        db, user.id, previous_marksheet, 'marksheet',
        application_id = scholarship_application.id, 
        file_name_prefix = 'previous_sem'
    )
    
    return {
        'message': 'Your application is submitted',
        'application_id': scholarship_application.id,
        'latest_marksheet': uploaded_latest_marksheet.file_name,
        'previous_marksheet': uploaded_previous_marksheet.file_name
    }

# @router.post('/apply_scholarship')
# async def apply(
#     scholarship_form: schemas.RequestScholarship = Form(...)
# ):
#     return scholarship_form
    
