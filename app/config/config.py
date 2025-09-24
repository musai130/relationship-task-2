from pydantic import BaseModel, PostgresDsn
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False


class DatabaseConfig(BaseModel):
    url: str
    echo: bool = False
    future: bool = True


# class DatabaseConfig(BaseModel):
#     url: PostgresDsn
#     echo: bool = True
#     echo_pool: bool = False
#     pool_size: int = 50
#     max_overflow: int = 10


class UrlPrefix(BaseModel):
    prefix: str = "/api"
    test: str = "/test"
    posts: str = "/posts"
    recipe: str = "/recipe"
    ingredient: str = "/ingredient"
    cuisine: str = "/cuisine"
    allergen: str = "/allergen"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    url: UrlPrefix = UrlPrefix()
    db: DatabaseConfig


settings = Settings()
