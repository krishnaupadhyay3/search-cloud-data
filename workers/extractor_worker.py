from tika import parser
from .database import es_client, redisClient
from pathlib import Path
from datetime import datetime


def extract_data(file_path, file_id, file_url):
    data = {}
    parsed = parser.from_file(file_path)

    data["file_name"] = Path(file_path).name
    data["text"] = parsed["content"]
    data["date"] = datetime.utcnow()
    data["url"] = file_url
    value = es_client.index(index="articles", body=data)
    redis_data = redisClient.hgetall(file_id)

    if value.get("result") == "created":
        redis_data["extracted"] = "success"
    else:
        redis_data["extracted"] = "failed"
    redisClient.hmset(file_id, redis_data)