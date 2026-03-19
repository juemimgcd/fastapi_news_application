from fastapi import FastAPI
from contextlib import asynccontextmanager
from conf.db_conf import engine
from routers import admin, news,users,history,favorite


@asynccontextmanager
async def lifespan(app: FastAPI):
    # async with engine.begin() as cnn:
    #     await cnn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(news.router)
app.include_router(users.router)
app.include_router(history.router)
app.include_router(favorite.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
