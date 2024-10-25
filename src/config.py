from pydantic import BaseSettings


class EmailCredentials(BaseSettings):

    email_id: str 
    email_password: str 
    email_server_port: int

    class Config:
        env_file = '.env'

class AppConfig(BaseSettings):

    app_host: str 
    app_port: int

    class Config:
        env_file = '.env'


class DBCredentials(BaseSettings):
    db_username: str
    db_password: str
    db_name: str 
    db_host: str = 'localhost'

    class Config:
        env_file = '.env'

class OAuth2Credentials(BaseSettings):
    secret_key: str 
    access_token_expire_minutes: int 
    algorithm: str 

    class Config:
        env_file = '.env'

class SerializerConfig(BaseSettings):

    reset_password_secret_key: str
    reset_password_salt: str 
    reset_password_token_expire_in_sec: int

    class Config:
        env_file = '.env'

class FileEnCryptorConfig(BaseSettings):
    file_encryption_key: str 

    class Config:
        env_file = '.env'



db_credentials = DBCredentials()

email_cred = EmailCredentials()

app_cred = AppConfig()

oauth2_credentials = OAuth2Credentials()

serializer_config = SerializerConfig()

file_encryptor_config = FileEnCryptorConfig()