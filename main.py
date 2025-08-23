from fastapi import FastAPI

import routes, modules


app = FastAPI()

app.include_router(routes.agent_route.router)
app.include_router(routes.test.router)
