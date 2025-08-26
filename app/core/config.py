from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "GradInsight 毕业季数据分析平台"
    APP_VERSION: str = "1.0.1"
    APP_DESCRIPTION: str = "专注毕业季小红书数据分析的智能分析平台"
    DEBUG: bool = False

    # MySQL数据库配置
    MYSQL_HOST: str = Field(default="localhost")
    MYSQL_PORT: int = Field(default=4000)
    MYSQL_USER: str = Field(default="root")
    MYSQL_PASSWORD: str = Field(default="")
    MYSQL_DATABASE: str = Field(default="gradinsight")
    MYSQL_CHARSET: str = Field(default="utf8mb4")

    # 数据库表配置
    MYSQL_POST_TABLE: str = Field(default="posts")
    MYSQL_TASK_TABLE: str = Field(default="tasks")
    MYSQL_COMMENT_TABLE: str = Field(default="comments")

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
    CONSUL_HOST: str = Field(default="localhost")
    CONSUL_PORT: int = Field(default=8500)
    CONSUL_SERVICE_KEY: str = Field(default="consul-crawler.rpc")

    # 爬虫服务配置
    CRAWLER_HOST: str = Field(default="localhost")
    CRAWLER_PORT: int = Field(default=8999)
    GRPC_TIMEOUT: int = Field(default=30)
    GRPC_MAX_RETRIES: int = Field(default=3)

    # CORS配置
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置单例"""
    return Settings()