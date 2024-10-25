from fastapi import APIRouter, Body, HTTPException, UploadFile, File, Depends, status
from fastapi.responses import FileResponse, StreamingResponse
from encrypt import encrypt_file_content, decrypt_file_content
from oauth2 import get_current_user
import schemas, models
from sqlalchemy.orm import Session 
from database import get_db
from operations.users_service import get_user_by_id, upload_user_document, get_user_document
import io
from typing import Literal


router = APIRouter(
    prefix='/users/documents',
    tags = ['Documents']
)




@router.post('/uploads')
async def upload_documents(
    document_type: Literal['passbook', 'marksheet'] = Body(...),
    user: schemas.TokenData = Depends(get_current_user),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    file_type = file.content_type
    if file_type != 'application/pdf':
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = f'Please upload PDF files, {file_type} is not acceptable.'
        )

    exisited_document: models.Docuemnts = await get_user_document(user.id, document_type, db)

    if exisited_document:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Document already uploaded..'
        )
    # Need to fix: User can only upload  each document_type only once.

    document: models.Documents = await upload_user_document(db, user.id, file, document_type)

    return {
       'message': 'File is encrypted and stored in Database', 
       'file_name': document.file_name
    }    





@router.get('/view', response_class = StreamingResponse)
async def view_uploaded_document(
    document_type: Literal['passbook', 'marksheet'],
    user: schemas.TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # document: models.Documents | None = db.query(models.Documents).filter(models.Documents.student_id == 12).filter(models.Documents.file_name.ilike(f"%{document_type}%")).first()
    # document: models.Documents | None = db.query(models.Documents)\
    #             .filter(models.Documents.student_id == user.id)\
    #             .filter(models.Documents.file_name.ilike(f"%{document_type}%"))\
    #             .first()
    document: models.Documents | None = await get_user_document(user.id, document_type, db)

    if not document:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'No uploads found'
        )
    
    #decrypt the file 
    decrypted_data: bytes = decrypt_file_content(document.encrypted_data)
    # Techncical stuff
    #   decrypted data is a single bytes object/single block of data which is not suitable for streaming...
    #   it is used only when the whole content in memomry like writing it into any files like pdf..
    #   we want to Stream the Data instead of wriring and saving the data in locally, For streaming
    #   the bytes should be iterable. 

    pdf_stream = io.BytesIO(decrypted_data) # convert the decrtypted bytes into io bytes
    # Technical stuff
    #   We use BytesIO it provides a interface that the bytes or treated as file-like object incrementally
    #   in memory that is suitable for Streaming to Client.. It makes the single bytes object iterable
    #   thats easy for rendering / Streaming the file.


    return StreamingResponse(
        pdf_stream,
        media_type='application/pdf',
        headers={
            "Content-Disposition": f"inline; filename={document.file_name}"
        }) 
