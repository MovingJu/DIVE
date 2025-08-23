from fastapi import FastAPI

import routes, modules


app = FastAPI()

app.include_router(routes.test.router)
