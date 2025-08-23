from dotenv import load_dotenv
import os
import requests
import numpy as np
import modules

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
    url='https://apis-navi.kakaomobility.com/v1/directions'
    headers={"Authorization":f'KakaoAK {kakao_api_key}','Content-Type':'application/json'}
    query=''
    if(waypoints):
        query={'orgiin':origin,'destination':destination,'waypoints':waypoints,'alternatives':'true'}
    else:
        query={'origin':origin,'destination':destination,'alternatives':'true'}
    result=requests.get(url=url,headers=headers,params=query)
    return result.json()

async def getVertexes(origin,destination,waypoints=[]):
    result=await getroutes(origin,destination,waypoints)
    results=[]
    for route in result['routes']:
        vertexes=[]
        for section in route['sections']:
            for road in section['roads']:
                vertexes.extend(road['vertexes'])
        results.append(vertexes)
    return results
            

async def getDistance(origin,destination,waypoints=[]):
    result=await getroutes(origin,destination,waypoints)
    return [i['summary']['distance'] for i in result['routes']]