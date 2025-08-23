from dotenv import load_dotenv
import os
import requests
import numpy as np
import httpx
import asyncio

load_dotenv()
kakao_api_key=os.getenv('KAKAO_API_KEY')
data_api_key=os.getenv('DATA_API_KEY')

async def getxyFromAdress(adress : str):
    url='https://dapi.kakao.com/v2/local/search/address.json'
    headers={"Authorization":f'KakaoAK {kakao_api_key}'}
    query={'query':adress}
    result=requests.get(url=url,headers=headers,params=query)
    return {'x':result.json()['documents'][0]['x'],'y':result.json()['documents'][0]['y']}


async def geyAdressFromxy(x:float,y:float):
    url='https://dapi.kakao.com/v2/local/geo/coord2address.json'
    headers={"Authorization":f'KakaoAK {kakao_api_key}'}
    query={'x':x,'y':y}
    result=requests.get(url=url,headers=headers,params=query)
    return result.json()['documents'][0]['road_address']['address_name']

async def getroutes(origin, destination, waypoints=[]):
    url = 'https://apis-navi.kakaomobility.com/v1/directions'
    headers = {
        "Authorization": f'KakaoAK {kakao_api_key}',
        'Content-Type': 'application/json'
    }
    if waypoints:
        query = {
            'origin': origin,
            'destination': destination,
            'waypoints': ','.join(waypoints),  # waypoints가 리스트면 문자열로 변환 필요
        }
    else:
        query = {
            'origin': origin,
            'destination': destination,
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=query)
        response.raise_for_status()
        return response.json()


async def getVertexes(origin,destination,waypoints=[]):
    result=await getroutes(origin,destination,waypoints)
    results=[]
    for route in result['routes']:
        vertexes=[]
        for section in route['sections']:
            for road in section['roads']:
                vertexes.extend(road['vertexes'])
        results.append(vertexes)

    vertexes=[]
    for i in range(0,len(results[0]),2):
        vertexes.append((results[0][i],results[0][i+1]))
    return vertexes

async def getDistance(origin,destination,waypoints=[]):
    result=await getroutes(origin,destination,waypoints)
    return [i['summary']['distance'] for i in result['routes']]



async def getMulriDistance(origin,destinations):
    url='https://apis-navi.kakaomobility.com/v1/destinations/directions'
    headers={"Authorization":f'KakaoAK {kakao_api_key}','Content-Type':'application/json'}
    query={'origin':origin,'destinations':destinations,'radius':6000} 
    result= requests.post(url=url,headers=headers,json=query)
    distances=dict()
    for route in result.json()['routes']:
        distances[route['key']]=route['summary']['distance']
    return distances

async def getGPStoKeyword(gps: tuple[float, float]):
    keywords = ["아파트", "카페", "편의점"]
    headers={"Authorization":f"KakaoAK {os.getenv("KAKAO_MAP_API_KEY") or ""}"}
    url = f"https://dapi.kakao.com/v2/local/search/keyword.json"
    params={
        "x":gps[0],
        "y":gps[1],
        "radius":100
    }