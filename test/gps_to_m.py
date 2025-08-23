from pyproj import Transformer
from shapely.geometry import Polygon
import math

def gps_to_xy(gps_x: float, gps_y: float) -> tuple[float, float] :
    to_5181 = Transformer.from_crs("EPSG:4326", "EPSG:5181", always_xy=True)
    return to_5181.transform(gps_x, gps_y)

def xy_to_gps(x: float, y: float) -> tuple[float, float] :
    to_wgs = Transformer.from_crs("EPSG:5181", "EPSG:4326", always_xy=True)
    return to_wgs.transform(x, y)

# def rhombus_from_diagonal(lat1, lon1, lat2, lon2, area_m2):
#     """
#     두 GPS 좌표(lat1, lon1), (lat2, lon2)를 대각선 양 끝점으로 하는
#     면적이 area_m2인 마름모의 4개 꼭짓점을 반환합니다.
    
#     반환: [(lat, lon), (lat, lon), (lat, lon), (lat, lon)]
#     """

#     # 변환기 (WGS84 <-> UTM-K / EPSG:5181)
#     to_5181 = Transformer.from_crs("EPSG:4326", "EPSG:5181", always_xy=True)
#     to_wgs  = Transformer.from_crs("EPSG:5181", "EPSG:4326", always_xy=True)

#     # 좌표 변환 (경도, 위도 순서!!)
#     x1, y1 = to_5181.transform(lon1, lat1)
#     x2, y2 = to_5181.transform(lon2, lat2)

#     # 두 점 중점
#     Mx, My = (x1 + x2) / 2, (y1 + y2) / 2

#     # 첫 번째 대각선 벡터
#     dx, dy = x2 - x1, y2 - y1
#     d1 = math.hypot(dx, dy)  # 길이

#     # 필요한 다른 대각선의 절반 길이
#     h = area_m2 / d1

#     # 직교 벡터 (정규화 X)
#     nx, ny = -dy, dx
#     n_len = math.hypot(nx, ny)
#     nx, ny = nx / n_len, ny / n_len  # 단위벡터

#     # 나머지 두 꼭짓점
#     Bx, By = Mx + h * nx, My + h * ny
#     Dx, Dy = Mx - h * nx, My - h * ny

#     # 최종 꼭짓점들 (A, C, B, D 순)
#     verts_5181 = [(x1, y1), (x2, y2), (Bx, By), (Dx, Dy)]

#     # WGS84로 변환 (lat, lon 순)
#     verts_wgs = [to_wgs.transform(x, y)[::-1] for x, y in verts_5181]

#     return verts_wgs


# # === 사용 예시 ===
# verts = rhombus_from_diagonal(
#     35.1778640159138, 129.075643947596,
#     35.1690637154991, 129.136018268316,
#     area_m2=284_200
# )

# for lat, lon in verts:
#     print(lat, lon)

from pyproj import Transformer
import math

def distribute_points_variable(lat1, lon1, lat2, lon2, area_m2, step=500, max_per_line=9):
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

    # 다른 대각선 절반길이
    h = min(area_m2, (x1 - x2) ** 2 + (y1 - y2) ** 2) / d1

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


# === 사용 예시 ===
grid = distribute_points_variable(
    35.1778640159138, 129.075643947596,
    35.1690637154991, 129.136018268316,
    area_m2=284_200,
    step=500,
    max_per_line=20
)

tot = 0
for line in grid:
    tot += len(line)
    print(len(line))
print(f"total : {tot}")