from fastapi import APIRouter
import aiomysql
import modules

router = APIRouter(
    prefix="/db",
    tags=["testing db functions"]
)

@router.get("/select/{query}")
async def read_item(query: str):
    conn = await modules.get_connection()

    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(query)
        results = await cur.fetchall()

    conn.close()

    return {"query": query, "result" : results}

@router.get("/class_test/{table_name}")
async def class_test(table_name: str):
    db = await modules.Manage.create()
    df = await db.read_table(table_name)
    await db.close()

    return {"result": df.to_dict(orient="records")}