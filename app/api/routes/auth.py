from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.responses import Response
import logging

from app.api.models.user import User, UserCreate, UserCreateAdmin, UserLogin, Token, UserRole
from app.api.models.response import ResponseModel
from app.core.auth import get_current_user, get_user_service, get_admin_user
from app.core.config import get_settings
from app.services.user_service import UserService
from app.utils.auth import create_access_token

router = APIRouter(prefix="/api/auth", tags=["authentication"])
settings = get_settings()

# 添加调试日志
logger = logging.getLogger(__name__)


# 添加OPTIONS请求处理 - 解决CORS预检请求问题
@router.options("/register")
async def register_options():
    """处理注册接口的OPTIONS预检请求"""
    return Response(status_code=200)

@router.options("/login")
async def login_options():
    """处理登录接口的OPTIONS预检请求"""
    return Response(status_code=200)

@router.options("/register-admin")
async def register_admin_options():
    """处理管理员注册接口的OPTIONS预检请求"""
    return Response(status_code=200)


@router.post(
    "/register",
    response_model=User,
    summary="用户注册",
    description="""
    注册新的普通用户账户。
    
    注意事项:
    - 用户名必须统一，长度3-50个字符
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
    管理员用户不能通过此接口创建，必须由现有管理员通过专门的接口创建。
    """
    try:
        logger.info(f"收到注册请求： username={user_data.username}, email={user_data.email}")

        # 创建普通用户，强制设置为USER角色
        user_create_data = UserCreateAdmin(
            username=user_data.username,
            password=user_data.password,
            email=user_data.email,
            role=UserRole.USER  # 强制设置为普通用户
        )

        logger.info("开始创建用户...")
        user = await user_service.create_user(user_create_data)

        if user is None:
            logger.warning(f"用户创建失败: 用户名 {user_data.username} 已存在")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )

        logger.info(f"用户创建成功: {user.username} (ID: {user.id})")
        return user

    except HTTPException:
        # 直接重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"注册过程中发生未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


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
    用户登录并获取访问令牌。
    
    使用标准的用户名/密码进行身份验证。成功后将返回一个JWT访问令牌，
    此令牌应在后续请求的Authorization头中使用。
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
    )
):
    """
    用户登录接口 - 获取访问令牌

    使用真实的数据库验证用户凭据。
    """
    try:
        username = user_login.username
        password = user_login.password

        logger.info(f"收到登录请求: username='{username}'")

        # 使用单一长连接进行数据库查询
        from app.db.single_connection import db_cursor
        from app.utils.auth import verify_password

        # 查询用户信息 - 将数据库操作和业务逻辑分离
        user_record = None
        try:
            async with db_cursor() as cursor:
                query = "SELECT id, username, password_hash, email, role, is_active FROM users WHERE username = %s"
                await cursor.execute(query, (username,))
                user_record = await cursor.fetchone()
        except Exception as db_error:
            logger.error(f"数据库查询失败: {db_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="服务器内部错误，请稍后再试"
            )

        # 在数据库操作完成后进行业务逻辑验证
        if not user_record:
            logger.warning(f"登录失败: 用户不存在 - {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 解构查询结果
        user_id, db_username, password_hash, email, role, is_active = user_record

        # 验证密码
        if not verify_password(password, password_hash):
            logger.warning(f"登录失败: 密码错误 - {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 验证账户是否激活
        if not is_active:
            logger.warning(f"登录失败: 账户未激活 - {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="账户已被禁用，请联系管理员",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 创建访问令牌
        user_data = {
            "sub": db_username,
            "id": user_id,
            "role": role,
            "email": email
        }
        access_token = create_access_token(data=user_data)

        logger.info(f"用户登录成功: {username}")

        # 返回符合Token模型的响应格式
        return Token(
            access_token=access_token,
            token_type="bearer"
        )
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"登录过程中发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录处理过程中发生错误，请稍后再试",
        )


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
async def get_current_user_info(request: Request):
    """
    获取当前用户信息接口

    从数据库获取真实的用户信息。
    """
    try:
        # 从请求头获取Authorization
        authorization = request.headers.get("authorization")

        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = authorization.split(" ")[1]

        # 验证JWT令牌
        from app.utils.auth import verify_token
        from app.api.models.user import UserRole
        from app.db.single_connection import db_cursor
        from datetime import datetime

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

        # 从数据库获取用户信息，使用单一长连接
        async with db_cursor() as cursor:
            query = """
            SELECT id, username, email, role, is_active, created_at, updated_at 
            FROM users WHERE username = %s
            """
            await cursor.execute(query, (username,))
            user_record = await cursor.fetchone()

            if not user_record:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user_id, db_username, email, role, is_active, created_at, updated_at = user_record

            logger.info(f"用户信息获取成功: username={username}, role={role}")

            # 返回真实的用户信息
            return User(
                id=user_id,
                username=db_username,
                email=email,
                role=UserRole.ADMIN if role == "admin" else UserRole.USER,
                is_active=is_active,
                created_at=created_at,
                updated_at=updated_at
            )

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"获取用户信息过程中发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )
