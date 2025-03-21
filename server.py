from fastapi import FastAPI
from gradio import mount_gradio_app
from app import webapp


def demo_function(name: str):
    return f"Hello, {name}!"


app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {"msg": "litton7 is alive"}


app = mount_gradio_app(app, webapp, path="/")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
