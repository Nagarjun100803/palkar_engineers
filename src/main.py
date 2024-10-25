import time
from typing import Callable
from fastapi import Request, FastAPI, Response, status
from fastapi.responses import JSONResponse
from routers import auth, users, documents, admin_view, application
from exception import ScholarshipAPIError, EntityNotFoundError



app = FastAPI(
    title = 'Palkar Engineers',
    version = '0.1.0',
    description = 'Scholarship and Carrer guidence platform for Palkar students.'
)



app.include_router(auth.router)
app.include_router(application.router)
app.include_router(admin_view.router)
app.include_router(users.router)
app.include_router(documents.router)





@app.middleware('http')
async def add_process_time_header(request: Request, call_next):

    start_time = time.perf_counter()
    response: Response = await call_next(request)
    process_time = time.perf_counter() - start_time

    response.headers['X-Process-Time'] = str(process_time)

    return response

def create_exception_handler(status_code: int , initial_detail: str) -> Callable[[Request, ScholarshipAPIError], JSONResponse]:

    """
        This functions returns a callable object(means a function) 
        which is actual exception handlerthat takes 2 parameters 
        [Request and the ScholarshipAPIError(actual exception)] and the exception 
        handler handles the exception ane return the custom exception as a JSONResponse
    """
    
    detail: dict = {'message': initial_detail}

    async def exception_handler(_: Request, exc: ScholarshipAPIError) -> JSONResponse:
        if exc.message:
            detail['message'] = exc.message

        if exc.name :
            detail['message'] = f"{detail['message']} [{exc.name}]"

        return JSONResponse(
            status_code = status_code, content= {'detail': detail['message']}
        )
    
    return exception_handler
    

app.add_exception_handler(
        exc_class_or_status_code = EntityNotFoundError,
        handler = create_exception_handler(
            status_code = status.HTTP_404_NOT_FOUND, initial_detail= "Entity doesn't exist"
        )
)

