from redis.asyncio import Redis
from src.core.config import config_obj

JTI_EXPIRY = 3600

token_blocklist = Redis(
    host=config_obj.REDIS_HOST,
    port=config_obj.REDIS_PORT,
    db=0,
    decode_responses=True
)

async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY
    )

async def token_in_blocklist(jti: str) -> bool:
    value = await token_blocklist.get(jti)
    return value is not None
