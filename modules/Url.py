from urllib.parse import urlencode
from dotenv import load_dotenv
import os, httpx, asyncio

load_dotenv()

class Url:
    """
    단일 목적지 → GET
    다중 목적지 → POST
    """
    def __init__(self, origin: tuple[float, float], *destinations: tuple[float, float], angle: int | None = None, waypoints: list[tuple[float, float]] = [], **params) -> None:
        """
        origin: (lon, lat)
        destinations: (lon, lat) ... (여러 개 가능)
        """
        self.is_multi = len(destinations) > 1
        self.angle = angle
        self.params = params

        if not self.is_multi:
            # 단일 목적지 → GET
            self.base_url = "https://apis-navi.kakaomobility.com/v1/directions"
            if angle is None:
                self.origin = f"{origin[0]},{origin[1]}"
            else:
                self.origin = f"{origin[0]},{origin[1]},angle={angle}"
            self.destination = f"{destinations[0][0]},{destinations[0][1]}"
            self.waypoints = "|".join(f"{wp[0]},{wp[1]}" for wp in waypoints)
            self.query = {
                "origin": self.origin,
                "destination": self.destination,
                "waypoints": self.waypoints,
                "summary": params.get("summary", False),
                "priority": "RECOMMEND",
                "car_fuel": "GASOLINE",
                "car_hipass": "false",
                "alternatives": "false",
                "road_details": "false"
            }
        else:
            # 다중 목적지 → POST
            self.base_url = "https://apis-navi.kakaomobility.com/v1/destinations/directions"
            self.body = {
                "origin": {
                    "x": str(origin[0]),
                    "y": str(origin[1])
                },
                "destinations": [
                    {"x": str(lon), "y": str(lat), "key": str(i)}
                    for i, (lon, lat) in enumerate(destinations)
                ],
                "radius": params.get("radius", 7000),
                "priority": params.get("priority", "TIME")
            }

    def __str__(self):
        if self.is_multi:
            return self.base_url
        else:
            return f"{self.base_url}?{urlencode(self.query)}"


class Fetch:
    def __init__(self, *url: Url) -> None:
        self.headers = {
            "Authorization": f"KakaoAK {os.getenv('KAKAO_API_KEY') or ''}",
            "Content-Type": "application/json"
        }
        self.urls = url

    async def make_request(self, url: Url, client: httpx.AsyncClient):
        if url.is_multi:
            resp = await client.post(url.base_url, headers=self.headers, json=url.body)
        else:
            resp = await client.get(str(url), headers=self.headers)
        return resp.json()

    async def fetch_async(self):
        async with httpx.AsyncClient() as client:
            tasks = [self.make_request(url, client) for url in self.urls]
            results = await asyncio.gather(*tasks)
        return results


if __name__ == "__main__":
    async def main():
        # 단일 목적지 예제 (GET)
        single = Url((129.07509523457, 35.17992598569), (129.136018268316, 35.1690637154991))
        f1 = Fetch(single)
        print(await f1.fetch_async())

        # 다중 목적지 예제 (POST)
        # multi = Url((127.13144, 37.44134),
        #             (127.14112, 37.44558),
        #             (127.14192, 37.44017),
        #             radius=5000)
        # f2 = Fetch(multi)
        # print(await f2.fetch_async())

    asyncio.run(main())
