from fastapi import APIRouter, Depends, Query, HTTPException, Path
from typing import Any

from api.models.post import PostList
from api.models.user import User
from api.models.response import ResponseModel
from core.auth import get_active_user
from services.post_service import PostService

router = APIRouter(prefix="/api/posts", tags=["posts"])


def get_post_service() -> PostService:
    """依赖注入：获取帖子服务"""
    return PostService()  # 移除对mysql_pool的依赖


@router.get("", response_model=PostList)
async def list_posts(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        task_id: str = Query(None),
        keyword: str = Query(None),
        tag: str = Query(None),
        min_likes: int = Query(None, ge=0),
        service: PostService = Depends(get_post_service),
        current_user: User = Depends(get_active_user)  # 需要登录才能查看高校信息
):
    """获取帖子列表（需要登录）"""
    result = await service.get_posts(skip, limit, task_id, keyword, tag, min_likes)
    return result


@router.get("/hot", response_model=ResponseModel)
async def get_hot_posts(
        limit: int = Query(20, ge=1, le=100, description="返回的热门帖子数量"),
        min_score: float = Query(0.0, ge=0.0, description="最低热度分数"),
        service: PostService = Depends(get_post_service),
        current_user: User = Depends(get_active_user)
) -> ResponseModel:
    """获取热门帖子列表（按热度分数排序）"""
    try:
        hot_posts = await service.get_hot_posts(limit, min_score)
        return ResponseModel(
            success=True,
            message="获取热门帖子成功",
            data={
                "posts": hot_posts,
                "total": len(hot_posts),
                "limit": limit,
                "min_score": min_score
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门帖子失败: {str(e)}")


@router.get("/{post_id}/hot-score", response_model=ResponseModel)
async def calculate_post_hot_score(
        post_id: str = Path(..., description="帖子ID"),
        service: PostService = Depends(get_post_service),
        current_user: User = Depends(get_active_user)
) -> ResponseModel:
    """计算单个帖子的热度分数"""
    try:
        hot_score = await service.calculate_hot_score(post_id)
        return ResponseModel(
            success=True,
            message="计算热度分数成功",
            data={
                "post_id": post_id,
                "hot_score": hot_score
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算热度分数失败: {str(e)}")


@router.post("/hot-scores/update-all", response_model=ResponseModel)
async def update_all_hot_scores(
        service: PostService = Depends(get_post_service),
        current_user: User = Depends(get_active_user)
) -> ResponseModel:
    """批量更新所有帖子的热度分数（管理员功能）"""
    # 检查用户权限
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以执行批量更新操作")
    
    try:
        result = await service.update_all_hot_scores()
        return ResponseModel(
            success=result["success"],
            message=result["message"],
            data={
                "updated_count": result["updated_count"]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量更新热度分数失败: {str(e)}")
