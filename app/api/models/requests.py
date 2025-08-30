from pydantic import BaseModel, Field


class CrawlRequest(BaseModel):
    keyword: str = Field(
        default="南昌大学",
        description="爬取关键词，例如：高校名称、专业名称",
        examples=["南昌大学", "计算机科学", "人工智能"]
    )
    site: int = Field(
        default=0,
        description="爬取站点(0:知乎, 1:微博, 2:小红书)",
        examples=[0, 1, 2],
        ge=0,
        le=2
    )
    post_count: int = Field(
        default=10,
        description="需要爬取的帖子数量，范围5-50",
        examples=[10, 20, 30],
        ge=5,
        le=50
    )
    include_comments: bool = Field(
        default=True,
        description="是否包含评论数据",
        examples=[True, False]
    )
    min_likes: int = Field(
        default=0,
        description="帖子最少点赞数，低于此数值的帖子将被过滤",
        examples=[0, 10, 50, 100],
        ge=0
    )
    comments_per_post: int = Field(
        default=10,
        description="每个帖子获取的评论数量，范围1-30",
        examples=[5, 10, 20],
        ge=1,
        le=30
    )
    comment_min_likes: int = Field(
        default=5,
        description="评论最少点赞数，低于此数值的评论将被过滤",
        examples=[0, 5, 10],
        ge=0
    )
    include_images: bool = Field(
        default=True,
        description="是否包含图片URL(可能增加爬取时间)",
        examples=[True, False]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "keyword": "南昌大学",
                "site": 0,
                "post_count": 20,
                "include_comments": True,
                "min_likes": 10,
                "comments_per_post": 10,
                "comment_min_likes": 5,
                "include_images": False
            }
        }
    }
