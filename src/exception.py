


class ScholarshipAPIError(Exception):

    """
        Base class for all the Exception in 'Palkar Engineers app'
    """
    def __init__(self, name: str = 'Palkar Engineers',
                  message: str = 'Service is unaivailable' ) -> None:
        self.name = name 
        self.message = message

        super().__init__(self.message, self.name)

    
class EntityNotFoundError(ScholarshipAPIError):
    """ Database returns nothing """
    pass 

