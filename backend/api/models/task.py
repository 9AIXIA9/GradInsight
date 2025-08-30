from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    RUNNING = "running"
    PENDING = "pending"
    DIVIDED = "divided"


class TaskListItem(BaseModel):
    task_id: str = Field(
        ...,
        description="任务的唯一标识符",
        examples=["task_12345"],
    )
    keyword: str = Field(
        ...,
        description="爬取的关键词",
        examples=["南昌大学", "计算机科学"],
    )
    site: int = Field(
        ...,
        description="爬取的平台(0:知乎, 1:微博, 2:小红书)",
        examples=[0, 1, 2],
    )
    status: TaskStatus = Field(
        ...,
        description="任务当前状态",
        examples=["completed", "running", "pending"],
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "task_id": "task_12345",
                "keyword": "南昌大学",
                "site": 0,
                "status": "completed",
                "created_at": "2025-08-30T10:00:00",
                "completed_at": "2025-08-30T10:05:30",
                "posts_collected": 20,
            }
        }
    }


class TaskDetail(TaskListItem):
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
    min_likes: int = Field(
        ...,
        description="帖子最少点赞数",
        examples=[0, 10, 50],
    )
    comments_per_post: int = Field(
        ...,
        description="每个帖子获取的评论数量",
        examples=[5, 10, 20],
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
    error_message: Optional[str] = Field(
        None,
        description="任务失败时的错误信息，成功则为null",
        examples=[None, "网络连接失败", "目标网站限制访问"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "task_id": "task_12345",
                "keyword": "南昌大学",
                "site": 0,
                "status": "completed",
                "created_at": "2025-08-30T10:00:00",
                "completed_at": "2025-08-30T10:05:30",
                "posts_collected": 20,
                "post_count": 20,
                "include_comments": True,
                "min_likes": 10,
                "comments_per_post": 10,
                "comment_min_likes": 5,
                "include_images": False,
                "error_message": None,
            }
        }
    }


class TaskList(BaseModel):
    tasks: List[TaskListItem] = Field(
        ...,
        description="任务列表",
        examples=[[]],
    )
    total: int = Field(
        ...,
        description="符合条件的任务总数",
        examples=[10, 25, 100],
    )
    page: int = Field(
        ...,
        description="当前页码，从1开始",
        examples=[1, 2, 3],
    )
    page_size: int = Field(
        ...,
        description="每页显示的任务数量",
        examples=[10, 20, 50],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "tasks": [
                    {
                        "task_id": "task_12345",
                        "keyword": "南昌大学",
                        "site": 0,
                        "status": "completed",
                        "created_at": "2025-08-30T10:00:00",
                        "completed_at": "2025-08-30T10:05:30",
                        "posts_collected": 20,
                    },
                    {
                        "task_id": "task_67890",
                        "keyword": "计算机科学",
                        "site": 1,
                        "status": "running",
                        "created_at": "2025-08-30T10:10:00",
                        "completed_at": None,
                        "posts_collected": 5,
                    },
                ],
                "total": 10,
                "page": 1,
                "page_size": 20,
            }
        }
    }
