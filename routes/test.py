from fastapi import APIRouter
import aiomysql
import modules
import pandas as pd
from dotenv import load_dotenv
import os
import requests
from starlette.responses import RedirectResponse
import httpx
import logging
from fastapi import Body

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
async def kakaologin(jwt : str=Body()):
    id = modules.decode_jwt_token(jwt)
    db = await modules.Manage.create()
    async with db.conn.cursor() as cursor:  
        await cursor.execute('SELECT user_type FROM users WHERE id = %s',(id,))
        result=await cursor.fetchall()
    df=pd.DataFrame(result,columns=['user_type'])
    await db.close()
    return {"result" : df.to_dict(orient='records')}
    
kakao_api_key = os.getenv("KAKAO_API_KEY")
redirect_uri = os.getenv("REDIRECT_URI")

@router.get("/kakao/authcode")
async def kakaoregister(code: str):
    # 1. Kakao API: 액세스 토큰 요청 (비동기)
    async with httpx.AsyncClient() as client:
        data = {
            'grant_type': 'authorization_code',
            'client_id': kakao_api_key,
            'redirect_uri': redirect_uri,
            'code': code,
        }
        resp = await client.post("https://kauth.kakao.com/oauth/token", data=data)
        try:
            resp.raise_for_status()
            token = resp.json().get('access_token')
            if not token:
                return {"error": "카카오 access token 발급 실패"}
        except Exception as e:
            return {"error": "카카오 token error", "detail": str(e)}

        # 2. Kakao API: 유저 정보 요청
        user_resp = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={'Authorization': f'Bearer {token}'}
        )
        try:
            userinfo = user_resp.json()
            userid = userinfo['id']
            username = userinfo['properties']['nickname']
            useremail = userinfo['kakao_account'].get('email', None)
        except Exception:
            return {'error': 'userinfo request error'}

    # 3. DB 연결 및 사용자 존재 확인 후 신규 등록
    db = await modules.Manage.create()
    try:
        async with db.conn.cursor() as cursor:
            await cursor.execute(
                'SELECT EXISTS(SELECT 1 FROM users WHERE id = %s) AS exist', (userid,)
            )
            result = await cursor.fetchone()
            exists = None
            if isinstance(result, dict) and 'exist' in result:
                exists = result['exist']
            elif result:
                exists = result[0]

            if not exists:
                await cursor.execute(
                    "INSERT INTO users (id, name, email, user_type) VALUES (%s, %s, %s, 0)",
                    (userid, username, useremail)
                )   
                await db.conn.commit()
    finally:
        await db.close()

    # 4. JWT 생성 및 Redirect 응답
    try:
        jwt_token = modules.create_jwt_token(userid)
    except Exception as e:
        return {"error": 'jwt error', "detail": str(e)}

    logging.info(username,jwt_token)
    return RedirectResponse(url=f"jasmap://oauth/kakao?JWT={jwt_token}")



    
    
    

  


