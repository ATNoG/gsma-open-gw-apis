from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    NEF_HOST: str = "http://localhost:8888"
    redis_geofencing_prefix: str = "geofencing_sub"


settings = Settings()
