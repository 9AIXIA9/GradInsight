import logging
from datetime import datetime
from typing import Optional

from api.models.user import User, UserCreateAdmin, UserRole
from core.config import get_settings
from utils.auth import get_password_hash, verify_password
from db.single_connection import db_cursor

logger = logging.getLogger(__name__)
settings = get_settings()


class UserService:
    def __init__(self, pool=None):
        # pool参数保留仅为兼容性，实际不再使用
        # 新的代码直接使用single_connection中的长连接
        pass

    async def create_user(self, user_data: UserCreateAdmin) -> Optional[User]:
        """创建用户 - 使用安全创建用户存储过程"""
        try:
            hashed_password = get_password_hash(user_data.password)

            # 使用安全的用户创建存储过程，自动处理重复检查和验证
            async with db_cursor() as cursor:
                # 调用安全创建用户存储过程
                await cursor.callproc('sp_create_user_safe', [
                    user_data.username,
                    user_data.email, 
                    hashed_password,
                    user_data.role.value,
                    '@result',  # OUT参数：结果信息
                    '@user_id'  # OUT参数：用户ID
                ])
                
                # 获取OUT参数结果
                await cursor.execute("SELECT @result, @user_id")
                result_row = await cursor.fetchone()
                
                if result_row:
                    result_msg, user_id = result_row
                    
                    if result_msg.startswith('SUCCESS') and user_id:
                        logger.info(f"用户创建成功: {user_data.username} (ID: {user_id})")
                        
                        # 查询创建的用户信息
                        await cursor.execute("""
                            SELECT username, email, role, is_active, created_at, updated_at 
                            FROM users WHERE id = %s
                        """, [user_id])
                        
                        user_row = await cursor.fetchone()
                        if user_row:
                            username, email, role, is_active, created_at, updated_at = user_row
                            return User(
                                id=user_id,
                                username=username,
                                email=email,
                                role=UserRole(role),
                                is_active=is_active,
                                created_at=created_at,
                                updated_at=updated_at
                            )
                    else:
                        # 存储过程返回错误信息
                        logger.warning(f"用户创建失败: {result_msg}")
                        return None
                
                return None
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

    async def get_user_statistics(self) -> Optional[dict]:
        """获取用户统计信息 - 使用视图"""
        try:
            async with db_cursor() as cursor:
                # 使用用户统计视图
                await cursor.execute("SELECT * FROM v_user_active_stats")
                stats_result = await cursor.fetchone()
                
                # 使用用户角色分布视图
                await cursor.execute("SELECT role, user_count, percentage FROM v_user_role_distribution")
                role_results = await cursor.fetchall()
                
                # 使用用户注册趋势视图（最近6个月）
                await cursor.execute("SELECT month, new_users FROM v_user_registration_trend LIMIT 6")
                trend_results = await cursor.fetchall()
                
                if stats_result:
                    total_users, active_users, inactive_users, active_rate = stats_result
                    
                    return {
                        "total_users": total_users,
                        "active_users": active_users,
                        "inactive_users": inactive_users,
                        "active_rate": active_rate,
                        "role_distribution": [
                            {"role": role, "count": count, "percentage": percentage}
                            for role, count, percentage in role_results
                        ],
                        "registration_trend": [
                            {"month": month, "new_users": new_users}
                            for month, new_users in trend_results
                        ]
                    }
                return None
        except Exception as e:
            logger.error(f"获取用户统计信息出错: {e}", exc_info=True)
            return None

    async def update_user_status(self, user_id: int, is_active: bool) -> bool:
        """更新用户状态 - 使用存储过程"""
        try:
            async with db_cursor() as cursor:
                await cursor.callproc('sp_user_update_status', [user_id, is_active])
                result = await cursor.fetchone()
                
                if result:
                    logger.info(f"用户状态更新成功: {result[0]}")
                    return True
                return False
        except Exception as e:
            logger.error(f"更新用户状态出错: {e}", exc_info=True)
            return False

    async def get_user_details_by_identifier(self, identifier: str) -> Optional[User]:
        """通过ID/用户名/邮箱获取用户详情 - 使用存储过程"""
        try:
            async with db_cursor() as cursor:
                await cursor.callproc('sp_user_get_details', [identifier])
                result = await cursor.fetchone()
                
                if result:
                    (user_id, username, email, role, is_active, created_at, updated_at, 
                     status_desc, role_desc, days_since_registration) = result
                     
                    return User(
                        id=user_id,
                        username=username,
                        email=email,
                        role=UserRole(role),
                        is_active=is_active,
                        created_at=created_at,
                        updated_at=updated_at
                    )
                return None
        except Exception as e:
            logger.error(f"获取用户详情出错: {e}", exc_info=True)
