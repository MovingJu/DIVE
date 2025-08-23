from pyproj import Transformer
from shapely.geometry import Polygon
import math

def gps_to_xy(gps_x: float, gps_y: float) -> tuple[float, float] :
    to_5181 = Transformer.from_crs("EPSG:4326", "EPSG:5181", always_xy=True)
    return to_5181.transform(gps_x, gps_y)

def xy_to_gps(x: float, y: float) -> tuple[float, float] :
    to_wgs = Transformer.from_crs("EPSG:5181", "EPSG:4326", always_xy=True)
    return to_wgs.transform(x, y)

def distribute_points_variable(lon1, lat1, lon2, lat2, area_m2, step=500, max_per_line=9):
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

    # ✅ 다른 대각선 절반길이
    d2 = (2 * area_m2) / d1
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
            line_points.append((lat, lon))
        else:
            for j in range(n_points):
                s = -w + (2 * w) * j / (n_points - 1)
                qx, qy = px + s * nx, py + s * ny
                lat, lon = to_wgs.transform(qx, qy)[::-1]
                line_points.append((lat, lon))

        result.append(line_points)

    return result

if __name__ == "__main__":
    # === 사용 예시 ===
    grid = distribute_points_variable(
        129.07509523457, 35.17992598569,
        129.136018268316, 35.1690637154991,
        area_m2=284_200,
        step=700,
        max_per_line=10
    )

    x, y = gps_to_xy(129.07509523457, 35.17992598569)
    a, b = gps_to_xy(129.136018268316, 35.1690637154991)
    distance = math.sqrt((x - a) ** 2 + (y - b) ** 2)
    print(f"distance : {distance} m")

    tot = 0
    tot_req = 1
    for line in grid:
        tot += len(line)
        tot_req *= len(line)
        print(len(line))
    print(f"total : {tot}")
    print(f"total minimun requests : {distance // 700}")