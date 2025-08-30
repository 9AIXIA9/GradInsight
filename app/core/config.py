from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = Field(...)
    APP_VERSION: str = Field(...)
    APP_DESCRIPTION: str = Field(...)
    DEBUG: bool = Field(default=False)

    # MySQL数据库配置
    MYSQL_HOST: str = Field(...)
    MYSQL_PORT: int = Field(...)
    MYSQL_USER: str = Field(...)
    MYSQL_PASSWORD: str = Field(default="")
    MYSQL_DATABASE: str = Field(...)
    MYSQL_CHARSET: str = Field(default="utf8mb4")

    # 数据库表配置
    MYSQL_POST_TABLE: str = Field(default="posts")
    MYSQL_TASK_TABLE: str = Field(default="tasks")
    MYSQL_COMMENT_TABLE: str = Field(default="comments")
    MYSQL_USER_TABLE: str = Field(default="users")

    # JWT认证配置
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # 分页配置
    DEFAULT_PAGE_SIZE: int = Field(default=20)
    MAX_PAGE_SIZE: int = Field(default=100)

    # 查询配置
    SEARCH_OPTIONS: str = Field(default="i")  # 不区分大小写

    # 排序配置
    POST_SORT_FIELD: str = Field(default="time")
    POST_SORT_ORDER: int = Field(default=-1)  # 降序
    COMMENT_SORT_FIELD: str = Field(default="time")
    COMMENT_SORT_ORDER: int = Field(default=-1)  # 降序

    # 评论配置
    COMMENTS_PER_POST: int = Field(default=20)

    # Consul配置
    CONSUL_HOST: str = Field(...)
    CONSUL_PORT: int = Field(...)
    CONSUL_SERVICE_KEY: str = Field(...)

    # 爬虫服务配置
    CRAWLER_HOST: str = Field(...)
    CRAWLER_PORT: int = Field(...)
    GRPC_TIMEOUT: int = Field(default=30)
    GRPC_MAX_RETRIES: int = Field(default=3)

    # CORS配置
    CORS_ORIGINS: str = Field(default="http://localhost:3000")

    @classmethod
    def parse_cors_origins(cls, v):
        """解析CORS origins字符串为列表"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置单例"""
    return Settings()