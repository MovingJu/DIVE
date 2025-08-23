from fastapi import APIRouter
import modules
import json


router = APIRouter(
    prefix="/agent",
    tags=["응급대원용 경로 조회"]
)

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

@router.get("/route/{user_id}/{gps1_x}/{gps1_y}/{gps2_x}/{gps2_y}")
async def route(user_id: int, gps1_x: float, gps1_y: float, gps2_x: float, gps2_y: float):
    single = modules.Url((gps1_x, gps1_y), (gps2_x, gps2_y))
    f1 = modules.Fetch(single)
    result = await f1.fetch_async()

    vertexes = extract_all_vertexes(result[0])  # result 안에서 vertexes 추출
    
    # DB 연결
    db = await modules.Manage.create()
    async with db.conn.cursor() as cursor:  
        # user_id는 로그인/요청자에 따라 바꿔 넣으셔야 함
        user_id = 1  

        # vertexes는 JSON으로 변환 후 저장
        await cursor.execute(
            "INSERT INTO AgentRoad (user_id, vertexes) VALUES (%s, %s)",
            (user_id, json.dumps(vertexes))
        )
        await db.conn.commit()   # INSERT 후 commit 필수!
    await db.close()

    return {"status": "success", "saved_vertexes": vertexes}
