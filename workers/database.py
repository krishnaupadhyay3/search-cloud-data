from redis import Redis
from elasticsearch import  Elasticsearch

es_client = Elasticsearch(hosts=["esprod1:9200"])
redisClient = Redis(host='redis-db')
