from pydantic import BaseSettings


class Settings(BaseSettings):
    db_hostname: str
    db_port: str
    db_password: str
    db_name: str
    db_username: str
    secret_key: str
    algorithm: str
    access_token_expire_min: int
    refresh_token_expire_day: int
    stream_delay_time: int
    # in the config file, the name of the parameters above has to be the same.
    class Config:
        env_file = ".env"


settings = Settings()
