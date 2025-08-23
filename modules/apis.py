from dotenv import load_dotenv
import os
import requests
import numpy as np

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
        query={'orgiin':origin,'destination':destination,'waypoints':waypoints,'alternatves':'true'}
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

    vertexes=[]
    for i in range(0,len(results[0]),2):
        vertexes.append((results[i],results[i+1]))
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
    import httpx
    keywords = ["아파트", "카페", "편의점"]
    headers = {
        "Authorization": f"KakaoAK {os.getenv('KAKAO_API_KEY') or ''}"
    }
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"

    closest = {
        "d": float("inf"),
        "x": None,
        "y": None
    }

    async with httpx.AsyncClient() as client:
        for kw in keywords:
            params = {
                "x": gps[0],
                "y": gps[1],
                "radius": 500,
                "query": kw,
                "sort": "distance"
            }
            response = await client.get(url, headers=headers, params=params)
            data = response.json()

            for doc in data.get("documents", []):
                dist = float(doc.get("distance", float("inf")))
                if dist < closest["d"]:
                    closest["d"] = dist
                    closest["x"] = float(doc["x"])
                    closest["y"] = float(doc["y"])
    return closest


if __name__ == "__main__":
    from asyncio import run
    async def main():
        result = await getGPStoKeyword((129.061903026452, 35.1946006301351))
        print(result)
    run(main())
    