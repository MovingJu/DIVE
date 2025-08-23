from fastapi import APIRouter
import aiomysql
import modules
import pandas as pd
from dotenv import load_dotenv
import os
import requests
from starlette.responses import RedirectResponse

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




@router.get('/data/adress/{adress}')
async def getadresstoxy(adress : str):
    result= await modules.getxyFromAdress(adress)
    return {"result":result}
    


@router.post("/kakao/authentication/")
async def kakaologin(jwt : str):
    id = modules.decode_jwt_token(jwt)
    db = await modules.Manage.create()
    async with db.conn.cursor() as cursor:  
        await cursor.execute('SELECT user_type FROM users WHERE id = %s',(id))
        result=await cursor.fetchall()
    df=pd.DataFrame(result,columns=['user_type'])
    await db.close()
    return {"result" : df.to_dict(orient='records')}
    


@router.get("/kakao/authcode")
async def kakaoregister(code : str):
    data = {
        'grant_type': 'authorization_code',  
        'client_id': os.getenv('KAKAO_API_KEY'),              
        'redirect_uri': os.getenv('REDIRECT_URI'),            
        'code': code     
    }

    # 카카오 인증 서버에 액세스 토큰 요청
    resp = requests.post("https://kauth.kakao.com/oauth/token", data=data)
    
    token=''
    try:
        token = resp.json()['access_token'] 
    except:
        return {"error":'카카오 token error'}


    headers = {
        'Authorization': 'Bearer ' + token  
    }

    user = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers)
    userinfo = ''
    userid = ''
    username=''
    useremail=''
    try:
        userinfo=user.json()
        userid=userinfo['id']
        username=userinfo['properties']['nickname']
        useremail=userinfo['kakao_account']['email']
    except:
        return {'error':'userinfo request error'}
          
    db = await modules.Manage.create()
    async with db.conn.cursor() as cursor:  
        await cursor.execute('SELECT EXISTS(SELECT 1 FROM users WHERE id = %s) AS exist',(userid))
        result=await cursor.fetchall()
    await db.close()
    if(result[0][0]):
        pass
    else:
        db = await modules.Manage.create()
        async with db.conn.cursor() as cursor:  
            await cursor.execute("INSERT INTO users (id, name, email, user_type) VALUES (%s, %s, %s,0)",(userid,username,useremail))
            result=await cursor.fetchall()
        await db.close()
    
    token = ''
    try:
        token = modules.create_jwt_token(userid)
        return RedirectResponse(url=f"jasmap://oauth/kakao?JWT={token}")
    except:
        return {"error":'jwt error'}



    
    
    

  


