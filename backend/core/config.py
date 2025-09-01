from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = Field(default="GradInsight")
    APP_VERSION: str = Field(default="1.0.0")
    APP_DESCRIPTION: str = Field(default="高校数据分析平台")
    DEBUG: bool = Field(default=False)

    # 服务器配置
    SERVER_HOST: str = Field(default="0.0.0.0")
    SERVER_PORT: int = Field(default=8000)
    RELOAD_ON_CHANGE: bool = Field(default=False)

    # MySQL数据库配置
    MYSQL_HOST: str = Field(default="localhost")
    MYSQL_PORT: int = Field(default=3306)  # MySQL默认端口
    MYSQL_USER: str = Field(default="root")
    MYSQL_PASS: str = Field(default="")
    MYSQL_DATABASE: str = Field(default="gradinsight")
    MYSQL_CHARSET: str = Field(default="utf8mb4")

    # 数据库表配置
    MYSQL_POST_TABLE: str = Field(default="posts")
    MYSQL_TASK_TABLE: str = Field(default="tasks")
    MYSQL_COMMENT_TABLE: str = Field(default="comments")
    MYSQL_USER_TABLE: str = Field(default="users")

    # JWT认证配置
    SECRET_KEY: str = Field(default="your-super-secret-key-here-change-in-production")  # 更安全的默认值
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # 分页配置
    DEFAULT_PAGE_SIZE: int = Field(default=20)
    MAX_PAGE_SIZE: int = Field(default=100)

    # ���询配置
    SEARCH_OPTIONS: str = Field(default="i")  # 不区分大小写

    # 排序配置
    POST_SORT_FIELD: str = Field(default="time")
    POST_SORT_ORDER: int = Field(default=-1)  # 降序
    COMMENT_SORT_FIELD: str = Field(default="time")
    COMMENT_SORT_ORDER: int = Field(default=-1)  # 降序

    # 评论配置
    COMMENTS_PER_POST: int = Field(default=20)

    # Consul配置
    CONSUL_HOST: str = Field(default="127.0.0.1")
    CONSUL_PORT: int = Field(default=8500)
    CONSUL_TIMEOUT: int = Field(default=5)
    CONSUL_SERVICE_KEY: str = Field(default="gradinsight")

    # 爬虫服务配置
    CRAWLER_SERVICE_NAME: str = Field(default="crawler-service")
    CRAWLER_HOST: str = Field(default="127.0.0.1")
    CRAWLER_PORT: int = Field(default=8999)
    GRPC_TIMEOUT: int = Field(default=30)
    GRPC_MAX_RETRIES: int = Field(default=3)

    # gRPC 连接配置
    GRPC_KEEPALIVE_TIME_MS: int = Field(default=30000)
    GRPC_KEEPALIVE_TIMEOUT_MS: int = Field(default=10000)
    GRPC_RETRY_DELAY: int = Field(default=1)

    # 数据库连接配置
    MYSQL_MAX_RETRIES: int = Field(default=2)
    MYSQL_RETRY_DELAY: float = Field(default=1.0)

    # 前端配置
    FRONTEND_HOST: str = Field(default="localhost")
    FRONTEND_PORT: int = Field(default=3000)

    # CORS配置
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000,http://127.0.0.1:3000,http://0.0.0.0:8000")

    # 开发环境配置
    DEV_AUTO_RELOAD: bool = Field(default=False)
    DEV_LOG_LEVEL: str = Field(default="INFO")

    # 统计数据默认值配置
    STATS_DEFAULT_POSTS_BOOST: int = Field(default=8500)
    STATS_DEFAULT_COMMENTS_BOOST: int = Field(default=42000)
    STATS_DEFAULT_SCHOOLS_COUNT: int = Field(default=285)
    STATS_DEFAULT_TASKS_COUNT: int = Field(default=96)

    def get_cors_origins(self):
        """解析CORS origins字符串为列表"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]
        return self.CORS_ORIGINS

    @property
    def frontend_url(self) -> str:
        """获取前端完整URL"""
        return f"http://{self.FRONTEND_HOST}:{self.FRONTEND_PORT}"

    @property
    def server_url(self) -> str:
        """获取服务器完整URL"""
        return f"http://{self.SERVER_HOST}:{self.SERVER_PORT}"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置单例"""
    return Settings()