from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body

from app.api.models.user import User, UserCreate, UserCreateAdmin, UserLogin, Token, UserRole
from app.core.auth import get_current_user, get_user_service, get_admin_user
from app.core.config import get_settings
from app.services.user_service import UserService
from app.utils.auth import create_access_token

router = APIRouter(prefix="/api/auth", tags=["authentication"])
settings = get_settings()


@router.post(
    "/register",
    response_model=User,
    summary="用户注册",
    description="""
    注册新的普通用户账户。
    
    注意事项:
    - 用户名必须唯一，长度3-50个字符
    - 密码至少6个字符
    - 邮箱必须符合标准格式且唯一
    - 所有新注册用户自动设置为普通用户(user)角色
    """,
    responses={
        200: {
            "description": "注册成功，返回用户信息",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "student2023",
                        "email": "student@university.com",
                        "role": "user",
                        "is_active": True,
                        "created_at": "2025-08-30T10:00:00",
                        "updated_at": "2025-08-30T10:00:00"
                    }
                }
            }
        },
        400: {
            "description": "用户名或邮箱已存在",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "用户名已存在"
                    }
                }
            }
        },
        422: {
            "description": "输入参数验证失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "username"],
                                "msg": "字符串长度应至少为3个字符",
                                "type": "value_error.any_str.min_length"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    用户注册接口 - 创建新的普通用户

    此接口用于创建新的普通用户账户，所有通过此接口注册的用户都自动设置为普通用户(user)角色。
    管理员账户不能通过此接口创建，必须由现有管理员通过专门的接口创建。
    """
    # 创建普通用户，强制设置为USER角色
    user_create_data = UserCreateAdmin(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        role=UserRole.USER  # 强制设置为普通用户
    )

    user = await user_service.create_user(user_create_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    return user


@router.post(
    "/register-admin",
    response_model=User,
    summary="创建管理员账户",
    description="""
    创建新的管理员账户（仅限现有管理员操作）。
    
    注意事项:
    - 必须使用管理员账户的JWT令牌进行授权
    - 用户名必须唯一，长度3-50个字符
    - 密码至少6个字符
    - 邮箱必须符合标准格式且唯一
    - 角色将强制设置为管理员(admin)角色
    """,
    responses={
        200: {
            "description": "创建成功，返回管理员用户信息",
            "content": {
                "application/json": {
                    "example": {
                        "id": 2,
                        "username": "adminuser",
                        "email": "admin@university.com",
                        "role": "admin",
                        "is_active": True,
                        "created_at": "2025-08-30T10:00:00",
                        "updated_at": "2025-08-30T10:00:00"
                    }
                }
            }
        },
        400: {
            "description": "用户名或邮箱已存在",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "用户名已存在"
                    }
                }
            }
        },
        401: {
            "description": "未提供有效的认证凭据",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "无效的认证凭据"
                    }
                }
            }
        },
        403: {
            "description": "权限不足，需要管理员权限",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "权限不足，需要管理员权限"
                    }
                }
            }
        }
    }
)
async def register_admin(
    user_data: UserCreateAdmin,
    user_service: UserService = Depends(get_user_service),
    current_admin: User = Depends(get_admin_user)  # 只有管理员才能创建管理员
):
    """
    创建管理员账户接口 - 仅限现有管理员操作

    此接口用于由现有管理员创建新的管理员账户。
    需要使用管理员JWT令牌进行授权，普通用户无法访问此接口。
    """
    # 强制设置为管理员角色
    user_data.role = UserRole.ADMIN

    user = await user_service.create_user(user_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="""
    用户使用用户名和密码登录系统，获取JWT访问令牌。
    
    支持两种方式提交登录请求:
    - 表单方式(Content-Type: application/x-www-form-urlencoded)
    - JSON格式(Content-Type: application/json)
    
    返回的Token可用于后续API调用的Authorization头(格式: Bearer {token})。
    """,
    responses={
        200: {
            "description": "登录成功，返回访问令牌",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "用户名或密码错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "用户名或密码错误"
                    }
                }
            }
        }
    }
)
async def login_user(
    user_login: UserLogin = Body(...,
        description="用户登录信息",
        examples=[{
            "username": "student2023",
            "password": "securepass123"
        }]
    ),
    user_service: UserService = Depends(get_user_service)
):
    """
    用户登录接口 - 获取访问令牌

    用户可以通过此接口使用用户名和密码登录系统，获取JWT访问令牌。
    登录成功后返回的令牌可用于访问需要认证的接口。
    """
    username = user_login.username
    password = user_login.password

    user = await user_service.authenticate_user(username, password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=User,
    summary="获取当前用户信息",
    description="""
    获取当前登录用户的详细信息。
    
    需要在请求头中提供有效的JWT令牌:
    Authorization: Bearer {token}
    """,
    responses={
        200: {
            "description": "成功获取用户信息",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "student2023",
                        "email": "student@university.com",
                        "role": "user",
                        "is_active": True,
                        "created_at": "2025-08-30T10:00:00",
                        "updated_at": "2025-08-30T10:00:00"
                    }
                }
            }
        },
        401: {
            "description": "未提供有效的认证凭据",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "无效的认证凭据"
                    }
                }
            }
        }
    }
)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息接口

    返回当前登录用户的详细信息，包括用户ID、用户名、邮箱、角色、激活状态和时间戳。
    需要使用有效的JWT令牌进行认证。
    """
    return current_user
