from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "御膳房"
    API_V1_STR: str = "/api"

    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "yushanfang"
    MYSQL_PASSWORD: str = "yushanfang123"
    MYSQL_DB: str = "yushanfang"
    SQLALCHEMY_DATABASE_URI: str | None = None

    JWT_SECRET: str = "yushanfang-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # 自定义 AI 配置（OpenAI 兼容接口）
    # 任何支持 OpenAI 格式的 AI 服务都可以配置
    AI_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    AI_API_KEY: str = ""
    AI_MODEL: str = "qwen-turbo"

    # 运行环境: development / production
    ENV: str = "development"

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
