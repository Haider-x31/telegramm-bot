import redis
from config import REDIS_URL

r = redis.from_url(REDIS_URL)

def get(url):
    return r.get(url)

def set(url, file_id):
    r.set(url, file_id)
