from fastapi import APIRouter
import modules

router = APIRouter(
    prefix="/agent",
    tags=["응급대원용 경로 조회"]
)

@router.get("/route/{gps1_x}/{gps1_y}/{gps2_x}/{gps2_y}")
async def route(gps1_x: float, gps1_y: float, gps2_x: float, gps2_y: float):
    single = modules.Url((gps1_x, gps1_y), (gps2_x, gps2_y))
    f1 = modules.Fetch(single)
    result = await f1.fetch_async()
    return result