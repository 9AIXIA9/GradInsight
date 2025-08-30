from fastapi import APIRouter, HTTPException, Request, Depends, Query

from app.api.models.task import TaskList, TaskDetail

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def get_task_service(request: Request):
    """依赖注入：获取任务服务"""
    from app.services.task_service import TaskService
    return TaskService(request.app.state.mysql_pool)


@router.get("", response_model=TaskList, summary="获取爬虫任务列表")
async def list_tasks(
        skip: int = Query(0, ge=0, description="跳过的记录数"),
        limit: int = Query(20, ge=1, le=100, description="返回的记录数量"),
        status: str = Query(None, description="任务状态过滤"),
        keyword: str = Query(None, description="关键词过滤"),
        service=Depends(get_task_service)  # 只有管理员才能查看任务列表
):
    """
    获取爬虫任务列表（仅限管理员）

    此接口用于获取系统中的爬虫任务列表，包含分页、状态过滤和关键词搜索功能。
    普通用户无权访问此接口，仅限管理员使用。
    """
    result = await service.get_tasks(skip, limit, status, keyword)
    return result


@router.get("/{task_id}", response_model=TaskDetail, summary="获取爬虫任务详情")
async def get_task(
        task_id: str,
        service=Depends(get_task_service)  # 只有管理员才能查看任务详情
):
    """
    获取爬虫任务详情（仅限管理员）

    此接口用于获取特定爬虫任务的详细信息。
    普通用户无权访问此接口，仅限管理员使用。
    """
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task
