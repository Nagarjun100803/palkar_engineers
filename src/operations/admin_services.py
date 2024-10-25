from sqlalchemy.orm import Session
import models



async def get_student_overview(student_id: int, db: Session):

    student_data_overview: tuple | None = db.query(

        models.PersonalInfo.first_name,
        models.PersonalInfo.gheru_naav,
        models.PersonalInfo.city,
        models.CollegeInfo.college_name,
        models.CollegeInfo.degree,
        models.CollegeInfo.branch,
        models.CollegeInfo.year_of_studying
    
    )\
        .select_from(models.PersonalInfo)\
        .join(models.ParentInfo, models.PersonalInfo.student_id == models.ParentInfo.student_id)\
        .join(models.CollegeInfo, models.PersonalInfo.student_id == models.CollegeInfo.student_id)\
        .filter(models.PersonalInfo.student_id == student_id)\
        .first()
    
    return student_data_overview
    


def get_application(db: Session, application_id: int | None = None) -> list[tuple] | None:
    """
        This function return all the application submitted by the students.

        Args:
            application_id(int) : Application ID of the particular application

        Returns:
            particular application if student_id is provided else it returns
            all the applications.
    """

    application_query = db.query(
        # Fetching some personal data
        models.PersonalInfo.first_name,
        models.PersonalInfo.last_name,
        models.PersonalInfo.mobile_num,
        models.PersonalInfo.gheru_naav,


        # Fetching all the attributes/columns from scholarship_applications table
        models.ScholarshipApplications.id,
        models.ScholarshipApplications.current_semester,
        models.ScholarshipApplications.latest_sem_cgpa,
        models.ScholarshipApplications.previous_sem_cgpa,
        models.ScholarshipApplications.difference_in_cgpa,
        models.ScholarshipApplications.parental_info,
        models.ScholarshipApplications.any_medical_issue,


        # Fetching some college info 
        models.CollegeInfo.degree,
        models.CollegeInfo.branch,
        models.CollegeInfo.college_name
        
    ).select_from(models.ScholarshipApplications)\
        .join(models.PersonalInfo, models.ScholarshipApplications.student_id == models.PersonalInfo.student_id)\
        .join(models.CollegeInfo, models.ScholarshipApplications.student_id == models.CollegeInfo.student_id)\
        
    if application_id:
        application: tuple | None = application_query.filter(models.ScholarshipApplications.id == application_id).first()
        return application
    
    applications: list[tuple] | None = application_query.all()

    return applications
