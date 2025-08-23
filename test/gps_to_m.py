from pyproj import Transformer
from shapely.geometry import Polygon
import math

def gps_to_xy(gps_x: float, gps_y: float) -> tuple[float, float] :
    to_5181 = Transformer.from_crs("EPSG:4326", "EPSG:5181", always_xy=True)
    return to_5181.transform(gps_x, gps_y)

def xy_to_gps(x: float, y: float) -> tuple[float, float] :
    to_wgs = Transformer.from_crs("EPSG:5181", "EPSG:4326", always_xy=True)
    return to_wgs.transform(x, y)

def distribute_points_variable(lon1, lat1, lon2, lat2, area_m2 = 8_842_000, step=1000, max_per_line=6):
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
            # 아파트 조회
            
            line_points.append((lat, lon))
        else:
            for j in range(n_points):
                s = -w + (2 * w) * j / (n_points - 1)
                qx, qy = px + s * nx, py + s * ny
                lat, lon = to_wgs.transform(qx, qy)[::-1]
                # 아파트 조회
                line_points.append((lat, lon))

        result.append(line_points)

    return result


import math
import heapq
import modules

# 코스트 캐시 저장소
_cost_cache = {}

async def cost(gps: tuple[float, float], layer_nodes: list[tuple[float, float]], layer: int, weight=1.0, **params):
    """
    gps: 현재 노드 (lat, lon)
    layer_nodes: 다음 레이어 전체 노드
    layer: 현재 레이어 인덱스
    반환: 각 노드별 비용 리스트
    """
    key = (gps, tuple(layer_nodes), layer)
    if key in _cost_cache:
        return _cost_cache[key]

    # 카카오 API 요청
    url = modules.Url(gps, *layer_nodes, radius=5000)
    f2 = modules.Fetch(url)
    results = await f2.fetch_async()

    print(f"results : {results}, current : {params.get("layers", None)}, {params["idxs"]}")

    dists = []
    routes = results[0].get("routes", None)

    if routes is None:  # 경로 실패
        dists = [float("inf")] * len(layer_nodes)
    else:
        for r in routes:
            d = r.get("summary", {}).get("distance", float("inf"))
            dists.append(d + layer * weight)

    _cost_cache[key] = dists
    return dists


async def shortest_path(tree, weight=0.2):
    """
    tree: [[(lat, lon)], [(lat, lon), ...], ..., [(lat, lon)]]
    시작층 → 마지막층 최소 비용 경로 탐색
    weight: 층 가중치 (크면 깊을수록 코스트가 더 커짐)
    """
    n_layers = len(tree)
    start = (0, 0)   # (layer, index)
    goal_layer = n_layers - 1

    # (누적 비용, layer, idx, 경로)
    pq: list[tuple[float, int, int, list]] = [(0, start[0], start[1], [tree[start[0]][start[1]]])]
    visited = list()

    while pq:
        total_cost, layer, idx, path = heapq.heappop(pq)

        # 목표 도달
        if layer == goal_layer:
            return path, visited

        if (layer, idx) in visited:
            continue
        visited.append((layer, idx))

        current = tree[layer][idx]

        next_layer_nodes = tree[layer + 1]
        costs = await cost(current, next_layer_nodes, layer, weight, layers=layer, idxs=idx)
        for j, (next_node, c) in enumerate(zip(next_layer_nodes, costs)):
            heapq.heappush(pq, (total_cost + c, layer + 1, j, path + [next_node]))

    return None  # 경로 없음



if __name__ == "__main__":
    # === 사용 예시 ===
    grid = distribute_points_variable(
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
    print(f"total minimun requests : {distance // 700 - 1}\ntotal maximum requests : {tot}")

    # async def main():
    #     print(await shortest_path(grid))
    # import asyncio
    # asyncio.run(main())