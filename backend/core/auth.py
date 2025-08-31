from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.models.user import User, UserRole
from services.user_service import UserService
from utils.auth import verify_token

# HTTP Bearer token认证
security = HTTPBearer()


async def get_user_service():
    """获取用户服务"""
    return UserService()  # 移除对连接池的依赖


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials

    # 验证JWT令牌
    token_data = verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = token_data.get("username")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 从数据库获取用户信息
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户（检查是否被禁用）"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    return current_user


async def get_admin_user(current_user: User = Depends(get_active_user)) -> User:
    """获取当前管理员用户（检查管理员权限）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user
