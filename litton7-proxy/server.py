from fastapi import FastAPI
from gradio import mount_gradio_app
from webui import webapp


app = FastAPI()
app = mount_gradio_app(app, webapp, path="/", show_api=False, show_error=False)


@app.get("/healthcheck")
def healthcheck():
    return "LCLab's chatbot proxy is alive."
