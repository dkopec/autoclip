from datetime import timedelta
from celery.result import AsyncResult
from fastapi import Body, FastAPI, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from worker import create_task, download_url
from connections import db_get, storage_get_url

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
    item_details = db_get(item_id)
    return JSONResponse(item_details)

@app.get("/video/{video_id}", response_class=HTMLResponse)
def get_details(request: Request, video_id): 
    item_details = db_get(video_id)
    return templates.TemplateResponse("video.html", context={"request": request, "video": item_details})

def minutes(num):
    return num * 60

@app.get("/download/{file_name}")
async def download_file(file_name: str):
    try:
        fileurl = storage_get_url(file_name)
        return JSONResponse(fileurl)
    except Exception as err:
        return {"message": "Error downloading file: {}".format(err)}