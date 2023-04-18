import redis

from celery.result import AsyncResult
from fastapi import Body, FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from worker import create_task, download_url, AutoClipVideo

db = redis.Redis(host='localhost', port=6379, db=0)
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request})


@app.post("/tasks", status_code=201)
def run_task(payload=Body(...)):
    task_type = payload["type"]
    task = create_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)


@app.post('/clip', status_code=201)
def clip(payload=Body(...)):
    print(payload)
    url = payload["url"]
    task = download_url.delay(str(url))
    return JSONResponse({"task_id": task.id})

@app.get("/details/{item_id}")
def get_details(item_id):
    item_details = db.hgetall(item_id)
    return JSONResponse(item_details)