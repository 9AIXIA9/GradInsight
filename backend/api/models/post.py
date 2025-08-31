from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Comment(BaseModel):
    id: str = Field(
        ...,
        description="评论的唯一标识符",
        examples=["comment_12345"]
    )
    commenter: str = Field(
        ...,
        description="评论者的用户名或ID",
        examples=["用户A", "张三"]
    )
    content: str = Field(
        ...,
        description="评论的具体内容",
        examples=["这是一条评论内容", "非常赞同楼主的观点"]
    )
    time: datetime = Field(
        ...,
        description="评论发布时间",
        examples=["2025-08-15T14:30:00"]
    )
    like_count: int = Field(
        ...,
        description="评论获得的点赞数",
        examples=[5, 10, 50]
    )
    reply_count: int = Field(
        ...,
        description="评论获得的回复数",
        examples=[0, 3, 10]
    )
    location: Optional[str] = Field(
        None,
        description="评论者的地理位置信息(若有)",
        examples=[None, "北京", "上海"]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "comment_12345",
                "commenter": "张三",
                "content": "南昌大学的计算机专业非常不错，实验条件很好",
                "time": "2025-08-15T14:30:00",
                "like_count": 15,
                "reply_count": 3,
                "location": "江西南昌"
            }
        }
    }


class Post(BaseModel):
    id: str = Field(
        ...,
        description="帖子的唯一标识符",
        examples=["post_67890"]
    )
    task_id: str = Field(
        ...,
        description="所属爬虫任务的唯一标识符",
        examples=["task_12345"]
    )
    title: str = Field(
        ...,
        description="帖子标题",
        examples=["南昌大学2025年招生情况", "计算机专业就业前景分析"]
    )
    poster: str = Field(
        ...,
        description="发帖人的用户名或ID",
        examples=["高校资讯", "学生李四"]
    )
    content: str = Field(
        ...,
        description="帖子的主要内容",
        examples=["这是帖子的详细内容...", "本文将分析计算机行业的发展趋势..."]
    )
    link: Optional[str] = Field(
        None,
        description="帖子的原文链接",
        examples=["https://www.xiaohongshu.com/explore/12345", "https://example.com/post/67890"]
    )
    time: datetime = Field(
        ...,
        description="帖子发布时间",
        examples=["2025-08-10T10:00:00"]
    )
    like_count: int = Field(
        ...,
        description="帖子获得的点赞数",
        examples=[50, 100, 500]
    )
    comment_count: int = Field(
        ...,
        description="帖子的评论总数",
        examples=[10, 25, 100]
    )
    collect_count: int = Field(
        ...,
        description="帖子被收藏的次数",
        examples=[5, 20, 80]
    )
    location: Optional[str] = Field(
        None,
        description="发帖人的地理位置信息(若有)",
        examples=[None, "江西南昌", "北京"]
    )
    tags: List[str] = Field(
        default_factory=list,
        description="帖子的标签列表",
        examples=[["高校", "招生"], ["计算机", "就业"]]
    )
    image_urls: List[str] = Field(
        default_factory=list,
        description="帖子包含的图片URL列表",
        examples=[["http://example.com/img1.jpg", "http://example.com/img2.jpg"]]
    )
    comments: List[Comment] = Field(
        default_factory=list,
        description="帖子的评论列表",
        examples=[[]]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "post_67890",
                "task_id": "task_12345",
                "title": "南昌大学2025年计算机专业招生情况分析",
                "poster": "高校资讯",
                "content": "南昌大学计算机科学与技术专业2025年计划招收本科生300人，较去年增加50人...",
                "link": "https://www.xiaohongshu.com/explore/12345",
                "time": "2025-08-10T10:00:00",
                "like_count": 156,
                "comment_count": 25,
                "collect_count": 42,
                "location": "江西南昌",
                "tags": ["高校", "招生", "计算机", "南昌大学"],
                "image_urls": ["http://example.com/img1.jpg", "http://example.com/img2.jpg"],
                "comments": [
                    {
                        "id": "comment_12345",
                        "commenter": "张三",
                        "content": "南昌大学的计算机专业非常不错，实验条件很好",
                        "time": "2025-08-15T14:30:00",
                        "like_count": 15,
                        "reply_count": 3,
                        "location": "江西南昌"
                    }
                ]
            }
        }
    }


class PostList(BaseModel):
    posts: List[Post] = Field(
        ...,
        description="帖子列表",
        examples=[[]]
    )
    total: int = Field(
        ...,
        description="符合条件的帖子总数",
        examples=[42, 100, 250]
    )
    page: int = Field(
        ...,
        description="当前页码，从1开始",
        examples=[1, 2, 3]
    )
    page_size: int = Field(
        ...,
        description="每页显示的帖子数量",
        examples=[10, 20, 50]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "posts": [
                    {
                        "id": "post_67890",
                        "task_id": "task_12345",
                        "title": "南昌大学2025年计算机专业招生情况分析",
                        "poster": "高校资讯",
                        "content": "南昌大学计算机科学与技术专业2025年计划招收本科生300人...",
                        "link": "https://www.xiaohongshu.com/explore/12345",
                        "time": "2025-08-10T10:00:00",
                        "like_count": 156,
                        "comment_count": 25,
                        "collect_count": 42,
                        "location": "江西南昌",
                        "tags": ["高校", "招生", "计算机", "南昌大学"],
                        "image_urls": ["http://example.com/img1.jpg"],
                        "comments": [
                            {
                                "id": "comment_12345",
                                "commenter": "张三",
                                "content": "南昌大学的计算机专业非常不错",
                                "time": "2025-08-15T14:30:00",
                                "like_count": 15,
                                "reply_count": 3,
                                "location": "江西南昌"
                            }
                        ]
                    },
                    {
                        "id": "post_67891",
                        "task_id": "task_12345",
                        "title": "计算机专业就业前景分析",
                        "poster": "就业指导中心",
                        "content": "随着人工智能的发展，计算机专业毕业生的就业前景更加广阔...",
                        "link": "https://www.xiaohongshu.com/explore/67891",
                        "time": "2025-08-09T16:20:00",
                        "like_count": 203,
                        "comment_count": 30,
                        "collect_count": 67,
                        "location": "北京",
                        "tags": ["就业", "计算机", "人工智能"],
                        "image_urls": [],
                        "comments": []
                    }
                ],
                "total": 42,
                "page": 1,
                "page_size": 20
            }
        }
    }
