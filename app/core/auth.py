from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.api.models.user import User, UserRole
from app.services.user_service import UserService
from app.utils.auth import verify_token
from app.db.mysql import connect_to_mysql

# HTTP Bearer token认证
security = HTTPBearer()


async def get_user_service():
    """获取用户服务"""
    pool = await connect_to_mysql()
    return UserService(pool)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """获取当前用户"""
    token = credentials.credentials

    # 验证token
    token_data = verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 获取用户信息
    user = await user_service.get_user_by_username(token_data["username"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """获取管理员用户（权限检查）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user


async def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    return current_user
