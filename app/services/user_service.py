import logging
from datetime import datetime
from typing import Optional

import aiomysql

from app.api.models.user import User, UserCreateAdmin, UserRole
from app.core.config import get_settings
from app.utils.auth import get_password_hash, verify_password

logger = logging.getLogger(__name__)
settings = get_settings()


class UserService:
    def __init__(self, pool: aiomysql.Pool):
        self.pool = pool

    async def create_user(self, user_data: UserCreateAdmin) -> Optional[User]:
        """创建��用户"""
        hashed_password = get_password_hash(user_data.password)

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # ���查用户名是否已存在
                check_sql = f"SELECT id FROM {settings.MYSQL_USER_TABLE} WHERE username = %s"
                await cursor.execute(check_sql, [user_data.username])
                if await cursor.fetchone():
                    return None  # 用户已存在

                # 检查邮箱是否已存在
                check_email_sql = f"SELECT id FROM {settings.MYSQL_USER_TABLE} WHERE email = %s"
                await cursor.execute(check_email_sql, [user_data.email])
                if await cursor.fetchone():
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

                return User(
                    id=user_id,
                    username=user_data.username,
                    email=user_data.email,
                    role=user_data.role,
                    is_active=True,
                    created_at=now,
                    updated_at=now
                )

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query_sql = f"""
                SELECT id, username, email, password_hash, role, is_active, created_at, updated_at
                FROM {settings.MYSQL_USER_TABLE}
                WHERE username = %s AND is_active = 1
                """

                await cursor.execute(query_sql, [username])
                row = await cursor.fetchone()

                if not row:
                    return None

                # 验证密码
                if not verify_password(password, row[3]):
                    return None

                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    role=UserRole(row[4]),
                    is_active=bool(row[5]),
                    created_at=row[6],
                    updated_at=row[7]
                )

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query_sql = f"""
                SELECT id, username, email, role, is_active, created_at, updated_at
                FROM {settings.MYSQL_USER_TABLE}
                WHERE username = %s AND is_active = 1
                """

                await cursor.execute(query_sql, [username])
                row = await cursor.fetchone()

                if not row:
                    return None

                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    role=UserRole(row[3]),
                    is_active=bool(row[4]),
                    created_at=row[5],
                    updated_at=row[6]
                )
