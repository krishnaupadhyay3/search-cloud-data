from fastapi import FastAPI, status, Response
from typing import  Optional
from models import InputString
from rq import Queue
from workers.database import  redisClient, es_client
from  workers.download_worker import  download_google_file, get_file_id

app = FastAPI()

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
