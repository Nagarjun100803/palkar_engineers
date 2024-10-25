from typing import Literal
from pydantic import BaseModel, EmailStr, conint, condecimal
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
    
class UserCreate(UserBase):
    role: Literal['user', 'admin'] = 'user'
    password: str 
    confirm_password: str

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True



class Token(BaseModel):
    access_token: str
    token_type: str = 'Bearer'

class TokenData(BaseModel):
    id: int
    role: str 



class PersonalInfo(BaseModel):
    first_name: str 
    last_name: str 
    mobile_num: str 
    gheru_naav: str 
    address: str 
    city: str
    pincode: str 

    class Config:
        orm_mode = True



class ParentInfo(BaseModel):

    father_name: str 
    father_occupation: str 
    mother_name: str 
    mother_occupation: str = 'Home Maker'
    parent_mobile_num: str 


class CollegeInfo(BaseModel):

    college_name: str  
    degree: Literal['BSc', 'BCA', 'BA', 'BE', 'MSc', 'MA', 'ME']
    branch: str 
    year_of_studying: int 
    college_address: str




class RequestScholarship(BaseModel):

    current_semester: conint(le=8, ge=1)  #type: ignore
    latest_sem_cgpa: condecimal(max_digits = 3, ge = 1, le = 10) #type: ignore
    previous_sem_cgpa: condecimal(max_digits = 3, ge = 1, le = 10) #type: ignore
    arrears_in_previous_sem: bool = False
    parental_info: Literal[
        'Both parents are alive',
        'Single Parent',
        'Both are passed away'
    ]
    any_medical_issue: bool = False

    class Config:
        orm_mode = True
    

class StudentVerifySchema(BaseModel):
    student_id: int    



    
    



