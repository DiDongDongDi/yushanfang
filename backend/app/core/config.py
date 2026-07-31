from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "御膳房"
    API_V1_STR: str = "/api"

    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DB: str = "yushanfang"
    SQLALCHEMY_DATABASE_URI: str | None = None

    JWT_SECRET: str = "yushanfang-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    AI_MODEL: str = "qwen-turbo"

    @property
    def DATABASE_URI(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
            f"?charset=utf8mb4"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
