import redis
from src import env

ACCESS_TOKEN_JTI_EXPIRY = 3600 # ttl of access token in the redis db

token_blacklist = redis.StrictRedis(
    host=env.REDIS_HOST,
    port=env.REDIS_PORT,
    db=0
)

def add_jti_to_blocklist(jti: str) -> None:    
    token_blacklist.set(
        name=jti,
        value=None,
        ex=ACCESS_TOKEN_JTI_EXPIRY
    )

def token_in_blocklist(jti: str) -> bool:
    response = token_blacklist.get(jti)
    return response is not None