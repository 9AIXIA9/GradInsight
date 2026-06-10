"""
GradInsight Analysis Service — 配置

只保留分析微服务需要的配置项：
- MySQL 连接
- 表名 / 分页 / 排序
- 服务器地址
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---- gRPC（Java 调用）----
    GRPC_PORT: int = Field(default=5001)

    # ---- Consul ----
    CONSUL_HOST: str = Field(default="127.0.0.1")
    CONSUL_PORT: int = Field(default=8500)
    CONSUL_SERVICE_NAME: str = Field(default="analysis-service")

    # ---- MySQL ----
    MYSQL_HOST: str = Field(default="localhost")
    MYSQL_PORT: int = Field(default=3306)
    MYSQL_USER: str = Field(default="root")
    MYSQL_PASS: str = Field(default="")
    MYSQL_DATABASE: str = Field(default="gradinsight")
    MYSQL_CHARSET: str = Field(default="utf8mb4")

    # ---- 表名 ----
    MYSQL_POST_TABLE: str = Field(default="posts")
    MYSQL_COMMENT_TABLE: str = Field(default="comments")

    # ---- 分页 ----
    DEFAULT_PAGE_SIZE: int = Field(default=20)
    MAX_PAGE_SIZE: int = Field(default=100)

    # ---- 排序 ----
    POST_SORT_FIELD: str = Field(default="time")
    POST_SORT_ORDER: int = Field(default=-1)
    COMMENT_SORT_FIELD: str = Field(default="time")
    COMMENT_SORT_ORDER: int = Field(default=-1)

    # ---- 评论 ----
    COMMENTS_PER_POST: int = Field(default=20)

    # ---- 调试 ----
    DEBUG: bool = Field(default=False)

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置单例"""
    return Settings()
