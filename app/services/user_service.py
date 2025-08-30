import logging
from datetime import datetime
from typing import Optional

from app.api.models.user import User, UserCreateAdmin, UserRole
from app.core.config import get_settings
from app.utils.auth import get_password_hash, verify_password
from app.db.single_connection import db_cursor

logger = logging.getLogger(__name__)
settings = get_settings()


class UserService:
    def __init__(self, pool=None):
        # pool参数保留仅为兼容性，实际不再使用
        # 新的代码直接使用single_connection中的长连接
        pass

    async def create_user(self, user_data: UserCreateAdmin) -> Optional[User]:
        """创建用户"""
        try:
            hashed_password = get_password_hash(user_data.password)

            # 使用单一长连接的游标进行查询
            async with db_cursor() as cursor:
                # 检查用户名是否已存在
                check_sql = f"SELECT id FROM {settings.MYSQL_USER_TABLE} WHERE username = %s"
                await cursor.execute(check_sql, [user_data.username])
                if await cursor.fetchone():
                    logger.warning(f"创建用户失败: 用户名已存在 - {user_data.username}")
                    return None  # 用户已存在

                # 检查邮箱是否已存在
                check_email_sql = f"SELECT id FROM {settings.MYSQL_USER_TABLE} WHERE email = %s"
                await cursor.execute(check_email_sql, [user_data.email])
                if await cursor.fetchone():
                    logger.warning(f"创建用户失败: 邮箱已存在 - {user_data.email}")
                    return None  # 邮箱已存在

                # 创建用户
                insert_sql = f"""
                INSERT INTO {settings.MYSQL_USER_TABLE} 
                (username, email, password_hash, role, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                now = datetime.now()
                await cursor.execute(insert_sql, [
                    user_data.username,
                    user_data.email,
                    hashed_password,
                    user_data.role.value,
                    True,
                    now,
                    now
                ])

                user_id = cursor.lastrowid
                logger.info(f"用户创建成功: {user_data.username} (ID: {user_id})")

                return User(
                    id=user_id,
                    username=user_data.username,
                    email=user_data.email,
                    role=user_data.role,
                    is_active=True,
                    created_at=now,
                    updated_at=now
                )
        except Exception as e:
            logger.error(f"创建用户出错: {e}", exc_info=True)
            raise

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户"""
        try:
            # 使用单一长连接的游标进行查询
            async with db_cursor() as cursor:
                query_sql = f"""
                SELECT id, username, email, password_hash, role, is_active, created_at, updated_at
                FROM {settings.MYSQL_USER_TABLE}
                WHERE username = %s AND is_active = 1
                """

                await cursor.execute(query_sql, [username])
                row = await cursor.fetchone()

                if not row:
                    logger.warning(f"验证用户失败: 用户不存在 - {username}")
                    return None

                # 验证密码
                if not verify_password(password, row[3]):
                    logger.warning(f"验证用户失败: 密码错误 - {username}")
                    return None

                logger.info(f"用户验证成功: {username}")
                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    role=UserRole(row[4]),
                    is_active=bool(row[5]),
                    created_at=row[6],
                    updated_at=row[7]
                )
        except Exception as e:
            logger.error(f"验证用户出错: {e}", exc_info=True)
            raise

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            # 使用单一长连接的游标进行查询
            async with db_cursor() as cursor:
                query_sql = f"""
                SELECT id, username, email, role, is_active, created_at, updated_at
                FROM {settings.MYSQL_USER_TABLE}
                WHERE username = %s
                """

                await cursor.execute(query_sql, [username])
                row = await cursor.fetchone()

                if not row:
                    logger.warning(f"获取用户失败: 用户不存在 - {username}")
                    return None

                # 检查结果行的长度是否足够
                if len(row) < 7:
                    logger.error(f"获取用户错误: 结果格式不正确 - {username}, 结果长度: {len(row)}")
                    return None

                logger.info(f"获取用户成功: {username}")

                try:
                    user = User(
                        id=row[0],
                        username=row[1],
                        email=row[2],
                        role=UserRole(row[3]) if row[3] else UserRole.USER,
                        is_active=bool(row[4]) if row[4] is not None else True,
                        created_at=row[5] if row[5] else datetime.now(),
                        updated_at=row[6] if row[6] else datetime.now()
                    )
                    return user
                except Exception as e:
                    logger.error(f"创建用户对象失败: {e}, 行数据: {row}", exc_info=True)
                    return None
        except Exception as e:
            logger.error(f"获取用户出错: {e}", exc_info=True)
            # 返回None而不是抛出异常，避免影响API响应
            return None
