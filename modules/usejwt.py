import datetime
from dotenv import load_dotenv
import os
import jwt

load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET_KEY') 
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600 

def create_jwt_token(id: str):
    payload = {
        'id': id,
        'exp': datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload['id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None