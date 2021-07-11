from fastapi import FastAPI, status, Response, Request
from typing import  Optional
from models import InputString
from rq import Queue
from workers.database import  redisClient, es_client
from  workers.download_worker import  download_google_file, get_file_id
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

urlQueue = Queue('googleDown', connection=redisClient)

request_body = {
       "mappings": {
         "properties": {
           "file": {
             "type":  "keyword"
           },
           "text": {
               "type": "text"
           },
           "date": {
                "type": "date"
            }
         }
       }
     }


def get_fields(data_dict):
    data = {}
    data["score"] = data_dict.get("_score")
    source = data_dict.get("_source")
    data["file_name"] = source.get("file_name")
    data["date"] = source.get("date")
    data["text"] = source.get("text")
    return data


@app.on_event("startup")
def app_startup():
    if not (es_client.indices.exists(index="articles")):
        es_client.indices.create(index="articles", body=request_body)


@app.post("/v1/driveurl")
def index_pdf(payload: InputString, response: Response):

    data_url = payload.dict()
    url_value = data_url.get("url")
    if not url_value:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"error": "url not correct"}
    try:
        file_id = get_file_id(url_value)
        if redisClient.hgetall(file_id):
            return {"error": "file already indexed"}
        redisClient.hmset(file_id, {"status": "inprogress"})
        urlQueue.enqueue_call(func=download_google_file,
                              args=(url_value,), job_id=file_id)
        return {"status": "success", "file_id": file_id}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}


@app.get("/v1/status/{file_id}")
def get_status(file_id: Optional[str] = None):
    if not file_id:
        return {}
    data = redisClient.hgetall(file_id)
    return data


@app.delete("/v1/status/{file_id}")
def delete_entry(file_id: Optional[str] = None):
    if not file_id:
        return {}
    data = redisClient.delete(file_id)
    return data


@app.get("/v1/search")
def search_index_api(request: Request, skip: int = 0, limit: int = 10,
                     q: str = None):
    query = q
    response_dict = {}
    if not query:
        return response_dict
    results = es_client.search(
        index="articles", body={"query": {"multi_match": {"query": query}}}
    )
    if results:
        response_dict["took"] = results.get("took", 0.0)
        response_dict["hits_count"] = results.get("hits")["total"]["value"]
        response_dict["hits"] = [get_fields(i) for i in
                                 results.get("hits")["hits"]]
    return response_dict


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search")
def search_index(request: Request, skip: int = 0, limit: int = 10,
                 q: str = None):
    query = q
    if not query:
        return templates.TemplateResponse("search.html", {"request": request,
                                          "result": None})
    results = es_client.search(
        index="articles", body={"query": {"multi_match": {"query": query}}}
    )
    result_for_template = {}

    if results:
        result_for_template["took"] = results.get("took", 0.0)
        result_for_template["hits_count"] = results.get(
                                            "hits")["total"]["value"]
        result_for_template["hits"] = results.get("hits")["hits"]

    return templates.TemplateResponse("search.html",
                                      {"request": request,
                                       "results": result_for_template})
