from datetime import datetime
from enum import IntEnum
from typing import Optional, List

from pydantic import BaseModel, Field


class TaskStatus(IntEnum):
    COMPLETED = 0  # 已完成
    FAILED = 1     # 失败
    RUNNING = 2    # 运行���
    STOPPED = 3    # 已停止
    PENDING = 4    # 等待中


class TaskListItem(BaseModel):
    id: str = Field(
        ...,
        description="任务的唯一标识符",
        examples=["task_12345"],
    )
    task_id: str = Field(
        ...,
        description="任务的唯一标识符(兼容字段)",
        examples=["task_12345"],
    )
    keyword: str = Field(
        ...,
        description="爬取的关键词",
        examples=["南昌大学", "计算机科学"],
    )
    site: str = Field(
        ...,
        description="爬取的平台",
        examples=["xiaohongshu", "zhihu", "weibo"],
    )
    post_count: int = Field(
        ...,
        description="请求爬取的帖子总数",
        examples=[10, 20, 30],
    )
    include_comments: bool = Field(
        ...,
        description="是否包含评论数据",
        examples=[True, False],
    )
    comments_per_post: int = Field(
        ...,
        description="每个帖子获取的评论数量",
        examples=[5, 10, 20],
    )
    min_likes: int = Field(
        ...,
        description="帖子最少点赞数",
        examples=[0, 10, 50],
    )
    comment_min_likes: int = Field(
        ...,
        description="评论最少点赞数",
        examples=[0, 5, 10],
    )
    include_images: bool = Field(
        ...,
        description="是否包含图片URL",
        examples=[True, False],
    )
    status: int = Field(
        ...,
        description="任务当前状态 (0:已完成, 1:失败, 2:运行中, 3:已停止, 4:等待中)",
        examples=[0, 1, 2, 3, 4],
    )
    created_at: datetime = Field(
        ...,
        description="任务创建时间",
        examples=["2025-08-30T10:00:00"],
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="任务完成时间，未完成则为null",
        examples=["2025-08-30T10:05:30"],
    )
    posts_collected: int = Field(
        0,
        description="已收集的帖子数量",
        examples=[0, 10, 20],
    )
    error_message: Optional[str] = Field(
        None,
        description="任务失败时的错误信息，成功则为null",
        examples=[None, "网络连接失败"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "task_12345",
                "task_id": "task_12345",
                "keyword": "南昌大学",
                "site": "xiaohongshu",
                "post_count": 20,
                "include_comments": True,
                "comments_per_post": 10,
                "min_likes": 0,
                "comment_min_likes": 0,
                "include_images": True,
                "status": 0,
                "created_at": "2025-08-30T10:00:00",
                "completed_at": "2025-08-30T10:05:30",
                "posts_collected": 20,
                "error_message": None,
            }
        }
    }


class TaskDetail(TaskListItem):
    """任务详情，继承TaskListItem的所有字段"""
    pass


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    tasks: List[TaskListItem] = Field(
        [],
        description="任务列表",
    )
    total: int = Field(
        0,
        description="任务总数",
        examples=[100],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "tasks": [
                    {
                        "id": "task_12345",
                        "task_id": "task_12345",
                        "keyword": "南昌大学",
                        "site": "xiaohongshu",
                        "post_count": 20,
                        "include_comments": True,
                        "comments_per_post": 10,
                        "min_likes": 0,
                        "comment_min_likes": 0,
                        "include_images": True,
                        "status": 0,
                        "created_at": "2025-08-30T10:00:00",
                        "completed_at": "2025-08-30T10:05:30",
                        "posts_collected": 20,
                        "error_message": None,
                    }
                ],
                "total": 1,
            }
        }
    }
