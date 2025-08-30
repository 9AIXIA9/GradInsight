from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/api/tasks", tags=["tasks-deprecated"])


@router.get("", summary="重定向到新的爬虫任务接口")
async def redirect_list_tasks():
    """重定向到新的爬虫任务列表接口"""
    return RedirectResponse(url="/api/crawler/tasks", status_code=301)


@router.get("/{task_id}", summary="重定向到新的爬虫任务详情接口")
async def redirect_get_task(task_id: str):
    """重定向到新的爬虫任务详情接口"""
    return RedirectResponse(url=f"/api/crawler/tasks/{task_id}", status_code=301)
