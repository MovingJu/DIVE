import asyncio
import modules

async def main():
    u = modules.Url((39.0, 127.0), (39.0, 127.0))
    print(u)

asyncio.run(main())