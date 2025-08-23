import aiomysql

from dotenv import load_dotenv
import os

load_dotenv()
async def get_connection():
    conn = await aiomysql.connect(
        host = os.getenv("DB_HOST"),
        port = int(os.getenv("DB_PORT")),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PW"), 
        db = os.getenv("DB_NAME"), 
        autocommit=True
    )
    return conn
