from pydantic import BaseModel, Field


class CrawlResponse(BaseModel):
    task_id: str = Field(
        ...,
        description="爬虫任务的唯一标识符，用于后续查询任务状态",
        examples=["task_12345", "f8d7e6c5-a4b3-12d1-9876-54321abcdef"],
    )
    success: bool = Field(
        ...,
        description="任务是否成功创建",
        examples=[True, False],
    )
    message: str = Field(
        ...,
        description="任务创建结果的详细说明",
        examples=["爬虫任务已成功创建", "创建任务失败：参数无效"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "task_id": "task_12345",
                "success": True,
                "message": "爬虫任务已成功创建，正在处理中，请稍后查询任务状态",
            }
        }
    }
