from sqlalchemy import(Column, String, Integer,
                       Float,TIMESTAMP, Boolean, text,
                        ForeignKey, LargeBinary)
from database import Base
# from sqlalchemy.orm import relationship


class Users(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, nullable = False, autoincrement = True)
    username = Column(String(50), nullable = False, unique = True)
    email = Column(String(60), nullable = False, unique = True)
    password = Column(String(60), nullable = False)
    role = Column(String, nullable = False, server_default = 'user')
    is_profile_completed = Column(Boolean, nullable = False, server_default = text('false'))
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default = text('now()'))

    #relationships

    # personal_info = relationship('PersonalInfo', back_populates = 'user', uselist = False, cascade = 'all, delete-orphan')



class PersonalInfo(Base):

    __tablename__ = 'personal_info'

    student_id = Column(Integer, ForeignKey('users.id', ondelete ='CASCADE'), primary_key = True)
    first_name = Column(String(30), nullable = False)
    last_name = Column(String(30), nullable = False)
    gheru_naav = Column(String(30), nullable = False)
    mobile_num = Column(String(10), nullable = False)
    address = Column(String(300), nullable = False)
    city = Column(String(30), nullable = False)
    pincode = Column(String(6), nullable = False)
    created_at = Column(TIMESTAMP(timezone = True), nullable = False, server_default = text('now()'))

    # user = relationship('Users', back_populates = 'personal_info')



class ParentInfo(Base):

    __tablename__ = 'parent_info'

    student_id = Column(Integer, ForeignKey('users.id', ondelete ='CASCADE'), primary_key = True)
    father_name = Column(String(50), nullable = False)
    father_occupation = Column(String(50), nullable = False)
    mother_name = Column(String(50), nullable = False)
    mother_occupation = Column(String(50), nullable = False)
    parent_mobile_num = Column(String(10), nullable = False)
    created_at = Column(TIMESTAMP(timezone = True), nullable = False, server_default = text('now()'))

    

class CollegeInfo(Base):

    __tablename__ = 'college_info'

    student_id = Column(Integer, ForeignKey('users.id', ondelete ='CASCADE'), primary_key = True)
    college_name = Column(String(300), nullable = False)
    degree = Column(String(10), nullable = False)
    branch = Column(String(200), nullable = False)
    year_of_studying = Column(Integer, nullable = False)
    college_address = Column(String(300), nullable = False)
    created_at = Column(TIMESTAMP(timezone = True), nullable = False, server_default = text('now()'))
    
    def __repr__(self) -> str:
        return f'Pursuing {self.degree} in th branch of {self.branch} at {self.college_name}.'


class Documents(Base):

    __tablename__ = 'student_documents'

    id = Column(Integer, primary_key = True)
    student_id = Column(Integer, ForeignKey('users.id'))
    document_type = Column(String(30), nullable = False)
    file_name = Column(String(30), nullable = False)
    encrypted_data = Column(LargeBinary, nullable = False)
    uploaded_at = Column(TIMESTAMP(timezone = True), nullable = False, server_default = text('now()'))

    def __repr__(self) -> str:
        return self.file_name
    

class ScholarshipApplications(Base):

    __tablename__ = 'scholarship_applications'

    id = Column(Integer, primary_key = True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    current_semester = Column(Integer, nullable = False)
    latest_sem_cgpa = Column(Float(3, asdecimal = True), nullable = False)
    previous_sem_cgpa = Column(Float(3, asdecimal = True), nullable = False)
    difference_in_cgpa = Column(Float(3, asdecimal= True), nullable = False)
    arrears_in_previous_sem = Column(Boolean, nullable = False, server_default = text('false'))
    parental_info = Column(String(350), nullable = False)
    status = Column(String(30), nullable = False, server_default = text('pending'))
    any_medical_issue = Column(Boolean, nullable = False, server_default = text('false'))
    requested_at = Column(TIMESTAMP(timezone = True), nullable = False, server_default = text('now()'))
    
    def __repr__(self) -> str:
        return f'Form id {self.id}, filled by {self.student_id}'


class Marksheets(Base):

    __tablename__ = 'marksheets'

    id = Column(Integer, primary_key = True)
    student_id = Column(Integer, ForeignKey('users.id'))
    application_id = Column(Integer, ForeignKey('scholarship_applications.id', ondelete='CASCADE'))
    encrypted_marksheet_data = Column(LargeBinary, nullable = False)
    file_name = Column(String, nullable = False)
    uploaded_at = Column(TIMESTAMP(timezone = True), nullable = False, server_default = text('now()'))

    def __repr__(self) -> str :
        return f'{self.file_name} uploaded by {self.student_id}'


    




# if __name__ == '__main__':
#     clg_info: CollegeInfo = CollegeInfo(
#         student_id = 12,
#         degree = 'BE',
#         branch = 'Computer Science and Engineering',
#         college_name = 'Hindusthan College of Engineering and Technology',
#         year_of_studying = 3,
#         college_address = '123 south street, Malumaachampatti, Coimbatore'
#         )
    
#     print(clg_info)