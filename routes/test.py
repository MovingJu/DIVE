from fastapi import APIRouter
import aiomysql
import modules
import pandas as pd

router = APIRouter(
    prefix="/db",
    tags=["testing db functions"]
)

@router.get("/select/{query}")
async def read_item(query: str):
    conn = await modules.get_connection()

    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(query)
        results = await cur.fetchall()

    conn.close()

    return {"query": query, "result" : results}

@router.get("/class_test/{table_name}")
async def class_test(table_name: str):
    db = await modules.Manage.create()
    df = await db.read_table(table_name)
    await db.close()

    return {"result": df.to_dict(orient="records")}


@router.post("kakao/login/")
async def kakaologin(name : str, email : str):
    db = await modules.Manage.create()
    async with db.conn.cursor() as cursor:  
        await cursor.execute('SELECT user_type FROM users WHERE name = %s AND email = %s',(name,email))
        result=await cursor.fetchall()
    df=pd.DataFrame(result,columns=['user_type'])
    await db.close()
    return {"result" : df.to_dict(orient='records')}
    
    
    

  






