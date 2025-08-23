from pyproj import Transformer
from shapely.geometry import Polygon
import math

def gps_to_xy(gps_x: float, gps_y: float) -> tuple[float, float] :
    to_5181 = Transformer.from_crs("EPSG:4326", "EPSG:5181", always_xy=True)
    return to_5181.transform(gps_x, gps_y)

def xy_to_gps(x: float, y: float) -> tuple[float, float] :
    to_wgs = Transformer.from_crs("EPSG:5181", "EPSG:4326", always_xy=True)
    return to_wgs.transform(x, y)

async def distribute_points_variable(lon1, lat1, lon2, lat2, area_m2 = 8_842_000, step=1000, max_per_line=6):
    """
    출발-도착을 대각선으로 하는 마름모 안에 점 배치.
    - 출발~도착을 step(m) 간격으로 분할
    - 분할선마다 폭에 비례하여 점 개수 변화 (처음/끝=적음, 중앙=많음)
    """

    # 변환기
    to_5181 = Transformer.from_crs("EPSG:4326", "EPSG:5181", always_xy=True)
    to_wgs  = Transformer.from_crs("EPSG:5181", "EPSG:4326", always_xy=True)

    # 좌표 변환
    x1, y1 = to_5181.transform(lon1, lat1)
    x2, y2 = to_5181.transform(lon2, lat2)

    # 대각선 벡터와 길이
    dx, dy = x2 - x1, y2 - y1
    d1 = math.hypot(dx, dy)

    if d1 == 0:
        raise ValueError("출발점과 도착점이 동일합니다.")

    d2 = (2 * area_m2) / d1
    print(d2)
    h = d2 / 2

    # 직교 단위벡터
    nx, ny = -dy / d1, dx / d1


    # 분할 개수
    n_div = int(d1 // step)

    result = []

    for i in range(n_div + 1):
        t = i / n_div if n_div > 0 else 0
        px, py = x1 + t * dx, y1 + t * dy

        # 현재 위치에서 마름모 반폭
        w = h * (1 - abs(2 * t - 1))

        # 점 개수 (최소 1개)
        n_points = max(1, round((w / h) * max_per_line))

        line_points = []
        if n_points == 1:
            qx, qy = px, py
            lat, lon = to_wgs.transform(qx, qy)[::-1]
            # gps = await modules.getGPStoKeyword((lon, lat))
            # lat, lon = gps['y'], gps['x']
            line_points.append((lon, lat))
        else:
            for j in range(n_points):
                s = -w + (2 * w) * j / (n_points - 1)
                qx, qy = px + s * nx, py + s * ny
                lat, lon = to_wgs.transform(qx, qy)[::-1]
                # gps = await modules.getGPStoKeyword((lon, lat))
                # lat, lon = gps['y'], gps['x']
                line_points.append((lon, lat))

        result.append(line_points)

    return result

def extract_all_vertexes(api_response: dict) -> list[tuple[float, float]]:
    """
    카카오 길찾기 API 결과에서 모든 vertexes를 하나의 리스트로 추출
    반환: [(lon, lat), (lon, lat), ...]
    """
    all_points = []

    routes = api_response.get("routes", [])
    for route in routes:
        sections = route.get("sections", [])
        for section in sections:
            roads = section.get("roads", [])
            for road in roads:
                vertexes = road.get("vertexes", [])
                # 2개씩 묶어서 (lon, lat) 추가
                for i in range(0, len(vertexes), 2):
                    all_points.append((vertexes[i], vertexes[i+1]))
    
    return all_points

import math
import heapq
import modules



# 코스트 캐시 저장소
_cost_cache = {}

async def cost(gps: tuple[float, float], next_node: tuple[float, float], layer: int, weight=20):
    """
    gps: 현재 노드 (lat, lon)
    next_node: 다음 레이어의 한 노드 (lat, lon)
    layer: 현재 레이어 인덱스
    반환: 단일 비용 값
    """
    key = (gps, next_node, layer)
    if key in _cost_cache:
        return _cost_cache[key][0]

    # 카카오 API 요청 (1대1)
    url = modules.Url(gps, next_node)
    f2 = modules.Fetch(url)
    results = await f2.fetch_async()

    vertexes = extract_all_vertexes(results[0])
    

    sobang_cost = len(set(vertexes) & set(sobang_vertexes))

    routes = results[0].get("routes", None)
    if routes is None:  # 경로 실패
        d = float("inf")
    else:
        d = routes[0].get("summary", {}).get("distance", float("inf"))

    cost_val = d + sobang_cost * weight + layer * weight * 10
    _cost_cache[key] = (cost_val, vertexes)
    return cost_val

async def shortest_path(tree, weight=0.2):
    n_layers = len(tree)
    start = (0, 0)
    goal_layer = n_layers - 1

    pq: list[tuple[float, int, int, list]] = [(0, start[0], start[1], [tree[start[0]][start[1]]])]
    visited = list()

    while pq:
        total_cost, layer, idx, path = heapq.heappop(pq)

        if layer == goal_layer:
            return path, visited

        if (layer, idx) in visited:
            continue
        visited.append((layer, idx))

        current = tree[layer][idx]
        next_layer_nodes = tree[layer + 1]

        for j, next_node in enumerate(next_layer_nodes):
            c = await cost(current, next_node, layer)
            heapq.heappush(pq, (c, layer + 1, j, path + [next_node]))

    return None

sobang_vertexes: list[tuple[float, float]] = []

if __name__ == "__main__":
    # === 사용 예시 ===
    async def main():

        global sobang_vertexes
        sobang_vertexes = await modules.getVertexes((129.105747814753, 35.1834432601063), (129.08586569729, 35.1893503587694))

        grid = await distribute_points_variable(
            129.061903026452, 35.1946006301351,
            129.115262179836, 35.1785037434279
        )

        x, y = gps_to_xy(129.061903026452, 35.1946006301351)
        a, b = gps_to_xy(129.115262179836, 35.1785037434279)
        distance = math.sqrt((x - a) ** 2 + (y - b) ** 2)
        print(f"distance : {distance} m")

        tot = 0
        tot_req = 1
        for line in grid:
            tot += len(line)
            tot_req *= len(line)
            print(len(line))
        print(f"total : {tot}")
        print(f"total requests : {tot_req}")

        vertexes, _ = await shortest_path(grid)
        print(vertexes)

    import asyncio
    asyncio.run(main())