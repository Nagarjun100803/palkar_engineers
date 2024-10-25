from cryptography.fernet import Fernet
from config import file_encryptor_config


fernet = Fernet(key = file_encryptor_config.file_encryption_key)


def encrypt_file_content(file_content: bytes) -> bytes | None:
    
    encrypted_document: bytes = fernet.encrypt(file_content)
    
    return encrypted_document

def decrypt_file_content(token: bytes) -> bytes | None:

    try :     

        decrypted_document: bytes = fernet.decrypt(token)
        return decrypted_document
    
    except Exception as e:
        return None

# if __name__ == '__main__':
    # encrypted_data = encrypt_file('test.txt')
    # print(encrypted_data)

    # enc_data: bytes = b'gAAAAABm1u7Zv_QWgIrn1wNbcW_ed5F3bhafdgF4v8ppHCOdQ6Td-Xer1kxh5oeOY6byyD5xarz4wMWkvFg9VVkaoimyxUhSgykZLWYmQZ4YQbKn0ZfTbUWe9pAEv7YQdzVbJbgcjaOS0H5IWf1xuYgsCRKcPiu-r6vPduuTwNKRnJtCpp1y_vemfQ7vDtiI16Tfvk3ncNl3WMN9gBtJrQXHilltHx3vgs-Bbys0JVBPCDXqpEEDG4MkxaZquhVENKGWU1xQLPsy-BFge52hvrw0akaqDoFCtzU6Aiy0hV79XzTLQnR98lYMigAnjZ9ZsjfdhwBEUeCqcodMocZRO-EJcCGJTSMm0-W94cYrRc9-0xWnBGixNrfEXJBobdk4MhipLSAit2vV64WJy1JrWpdJzsl8Br-WfMgNMHKf3JWbmbUoL_QcLv9ThDVV7SsQvoCNKFjBa3BdN4rpX_uDuSxcGlQyckPyjDo5IcwYAj72T72JCvd7tDFsbO5wDQeoHyYA_Z13qSrD5Gp5pvmOKvmdNzj-fxPF2fMQ5X6VGyBKjUY3pH50sO1bhy6MNDB763sHLH3277Z4'

    # decrypt_data = decrypt_file(enc_data)

    # print(decrypt_data)

