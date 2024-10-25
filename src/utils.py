from passlib.context import CryptContext
from itsdangerous.url_safe import URLSafeTimedSerializer
from config import serializer_config

# context to work with password functionalities like hashing and verifying
pwd_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')



# Serializer object to serialize and deserialize the user info in urls, useful for password-reset
serializer =  URLSafeTimedSerializer(
    secret_key = serializer_config.reset_password_secret_key,
    salt = serializer_config.reset_password_salt
)



def get_hash_password(raw_password: str) -> str : 
    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool :
    return pwd_context.verify(raw_password, hashed_password)


def create_token_for_reset(payload: dict):
    return serializer.dumps(payload)


def verify_token(token: str) -> dict | None:
    
    try:
        payload: dict = serializer.loads(token, max_age = serializer_config.reset_password_token_expire_in_sec)
    except Exception as e:
        return None
    
    return payload


