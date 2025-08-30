from fastapi import APIRouter, Request, Depends, Query

from app.api.models.post import PostList
from app.api.models.user import User
from app.core.auth import get_active_user

router = APIRouter(prefix="/api/posts", tags=["posts"])


def get_post_service(request: Request):
    """依赖注入：获取帖子服务"""
    from app.services.post_service import PostService
    return PostService(request.app.state.mysql_pool)


@router.get("", response_model=PostList)
async def list_posts(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        task_id: str = Query(None),
        keyword: str = Query(None),
        tag: str = Query(None),
        min_likes: int = Query(None, ge=0),
        service=Depends(get_post_service),
        current_user: User = Depends(get_active_user)  # 需要登录才能查看高校信息
):
    """获取帖子列表（需要登录）"""
    result = await service.get_posts(skip, limit, task_id, keyword, tag, min_likes)
    return result
