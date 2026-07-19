from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL:str
    SECRET_KEY:str
    TEST_DATABASE_URL:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    REFRESH_TOKEN_EXPIRE_DAYS:int
    BASE_URL:str
    REDIS_HOST:str
    REDIS_PORT:int
    
    model_config=SettingsConfigDict(env_file=".env")

settings=Settings()