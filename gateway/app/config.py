from pydantic_settings import BaseSettings
 
class Settings(BaseSettings):
    NEF_HOST: str = "http://localhost:8888"
    redis_SMSOTP_prefix: str = "SMSOTP"
 

settings = Settings()