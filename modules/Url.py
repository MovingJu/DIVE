from urllib.parse import urlencode
from dotenv import load_dotenv
import os, httpx, asyncio

load_dotenv()
class Url:
    """
    Url 조작을 위한 클래스. 별로 쓸 필요는 없음. 클린한 코드를 지향하는 당신 츄라이츄라이.
    """
    def __init__(self, origin: tuple[float, float], destination: tuple[float, float], angle: int | None = None, waypoints: list[tuple[float, float]] = [], **params) -> None:
        """
        ### 필수 쿼리
        - origin : 출발지점 GPS 좌표 튜플로 ()
        - destination : 도착지점 GPS 좌표 튜플로
        
        ### 부가 쿼리
        - angle : 출발 각도
        - waypoints : 경유지들 GPS좌표 리스트로 넣기

        ### 최적화 쿼리
        - summary : 총 거리 등등만 필요하면 이거 True로 하기
        """
        self.base_url = "https://apis-navi.kakaomobility.com/v1/directions"
        if angle is None:
            self.origin = f"{origin[0]},{origin[1]}"
        else:
            self.origin = f"{origin[0]},{origin[1]},angle={angle}"
        self.destination = f"{destination[0]},{destination[1]}"
        self.summary = params.get("summary", False)
        self.waypoints = "|".join(f"{wp[0]},{wp[1]}" for wp in waypoints)
        self.params = {
            "origin" : self.origin,
            "destination" : self.destination,
            "waypoints" : self.waypoints,
            "summary" : self.summary,
            "priority" : "RECOMMEND",
            "car_fuel" : "GASOLINE",
            "car_hipass" : "false",
            "alternatives" : "false",
            "road_details" : "false"
        }
        for key, val in params.items():
            self.params[key] = val

    def __str__(self):
        query = urlencode(self.params)
        return f"{self.base_url}?{query}"
    
    def set_params(self, **params: str):
        for key, val in params.items():
            self.params[key] = val

class Fetch:
    def __init__(self, *url: Url) -> None:
        self.headers = {
            "Authorization" : f"KakaoAK {os.getenv('KAKAO_API_KEY') or ''}"
        }
        self.urls = url
    
    @staticmethod
    async def make_request(url: Url, client: httpx.AsyncClient):
        response = await client.get(url.__str__())
        return response.json()
    
    async def fetch_async(self):
        async with httpx.AsyncClient() as client:
            tasks = [Fetch.make_request(url, client) for url in self.urls]
            results = await asyncio.gather(*tasks)
        return results

if __name__ == "__main__":
    async def main():
        url = [Url((37.402464820205246, 127.10764191124568),(37.39419693653072, 127.11056336672839)), Url((37.402464820205246, 127.10764191124568),(37.39419693653072, 127.11056336672839)), Url((37.402464820205246, 127.10764191124568),(37.39419693653072, 127.11056336672839))]
        print(url)
        f = Fetch(url[0], url[1], url[2])
        print(await f.fetch_async())
    asyncio.run(main())
