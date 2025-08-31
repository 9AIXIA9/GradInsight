from fastapi import APIRouter, HTTPException, Request, Depends, Query
from typing import Optional

from api.models.requests import CrawlRequest
from api.models.response import CrawlResponse
from api.models.task import TaskListResponse, TaskDetail
from api.models.user import User
from core.auth import get_admin_user
from core.config import get_settings
from services.crawler_service import CrawlerService
from services.task_service import TaskService
from utils.consul_discovery import ConsulServiceDiscovery, ConsulConfig

router = APIRouter(prefix="/api/crawler", tags=["crawler-management"])

# 获取设置
settings = get_settings()


def get_crawler_service() -> CrawlerService:
    """依赖注入：获取爬虫服务"""
    # 构建爬虫服务配置
    config = {
        "host": settings.CRAWLER_HOST,
        "port": settings.CRAWLER_PORT,
        "timeout": settings.GRPC_TIMEOUT,
        "max_retries": settings.GRPC_MAX_RETRIES
    }
    return CrawlerService(config)


def get_task_service() -> TaskService:
    """依赖注入：获取任务服务"""
    return TaskService()


def get_consul_discovery() -> ConsulServiceDiscovery:
    """依赖注入：获取Consul服务发现"""
    consul_config = ConsulConfig(
        host=settings.CONSUL_HOST,
        port=settings.CONSUL_PORT,
        timeout=settings.CONSUL_TIMEOUT
    )
    return ConsulServiceDiscovery(consul_config)


@router.post("/start", response_model=CrawlResponse, summary="启动爬虫任务")
async def start_crawl(
    request_data: CrawlRequest,
    crawler_service: CrawlerService = Depends(get_crawler_service),
    current_user: User = Depends(get_admin_user)  # 只有管理��可以启动爬虫任务
):
    """
    启动新的爬虫任务（仅管理员）

    此接口用于启动新的爬虫任务，只有管理员权限的用户才能调用。
    启动后会返回任务ID和状态信息。
    """
    try:
        result = await crawler_service.start_crawl(request_data.model_dump())
        return CrawlResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"爬虫服务调用失败: {str(e)}")


@router.get("/tasks", response_model=TaskListResponse, summary="获取爬虫任务列表")
async def list_tasks(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数量"),
    status: Optional[str] = Query(None, description="任务状态过滤"),
    keyword: Optional[str] = Query(None, description="关键词过滤"),
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_admin_user)  # 只有管理员才能查看任务列表
):
    """
    获取爬虫任务列表（仅限管理员）

    此接口用于获取系统中的爬虫任务列表，包含分页、状态过滤和关键词搜索功能。
    普通用户无权访问此接口，仅限管理员使用。
    """
    try:
        result = await task_service.get_tasks(skip, limit, status, keyword)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@router.get("/tasks/{task_id}", response_model=TaskDetail, summary="获取爬虫任务详情")
async def get_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_admin_user)  # 只有管理员才能查看任务详情
):
    """
    获取爬虫任务详情（仅限管理员）

    此接口用于获取特定爬虫任务的详细信息。
    普通用户无权访问此接口，仅限管理员使用。
    """
    try:
        task = await task_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务详情失败: {str(e)}")


@router.delete("/tasks/{task_id}", summary="删除爬虫任务")
async def delete_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_admin_user)  # 只有管理员才能删除任务
):
    """
    删除爬虫任务（仅限管理员）

    此接口用于删除指定的爬虫任务。
    普通用户无权访问此接口，仅限管理员使用。
    """
    try:
        success = await task_service.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="任务不存在")
        return {"message": "任务删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


@router.get("/status", summary="获取爬虫服务状态")
async def get_crawler_status(
    consul_discovery: ConsulServiceDiscovery = Depends(get_consul_discovery),
    current_user: User = Depends(get_admin_user)  # 只有管理员才能查看服务状态
):
    """
    获取爬虫服务状态（仅限管理员）

    此接口通过Consul服务发现来获取爬虫微服务的运行状态信息。
    普通用户无权访问此接口，仅限管理员使用。
    """
    try:
        # 通过Consul查询爬虫服务状态
        service_name = settings.CRAWLER_SERVICE_NAME
        status = consul_discovery.get_service_health(service_name)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取服务状态失败: {str(e)}")
