from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名，长度3-50个字符，唯一",
        examples=["student2023"]
    )
    password: str = Field(
        ...,
        min_length=6,
        description="密码，至少6个字符",
        examples=["securepass123"]
    )
    email: str = Field(
        ...,
        pattern=r'^[^@]+@[^@]+\.[^@]+$',
        description="有效的电子邮箱地址",
        examples=["student@university.com"]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "student2023",
                "password": "securepass123",
                "email": "student@university.com"
            }
        }
    }


class UserCreateAdmin(BaseModel):
    """管理员创建用户时使用的模型"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名，长度3-50个字符，唯一",
        examples=["adminuser"]
    )
    password: str = Field(
        ...,
        min_length=6,
        description="密码，至少6个字符",
        examples=["admin@123456"]
    )
    email: str = Field(
        ...,
        pattern=r'^[^@]+@[^@]+\.[^@]+$',
        description="有效的电子邮箱地址",
        examples=["admin@university.com"]
    )
    role: UserRole = Field(
        default=UserRole.USER,
        description="用户角色，admin或user",
        examples=["admin"]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "adminuser",
                "password": "admin@123456",
                "email": "admin@university.com",
                "role": "admin"
            }
        }
    }


class UserLogin(BaseModel):
    username: str = Field(
        ...,
        description="用户名",
        examples=["student2023"]
    )
    password: str = Field(
        ...,
        description="密码",
        examples=["securepass123"]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "student2023",
                "password": "securepass123"
            }
        }
    }


class User(BaseModel):
    id: int = Field(..., description="用户ID", examples=[1])
    username: str = Field(..., description="用户名", examples=["student2023"])
    email: str = Field(..., description="电子邮箱", examples=["student@university.com"])
    role: UserRole = Field(..., description="用户角色", examples=["user"])
    is_active: bool = Field(..., description="账户是否激活", examples=[True])
    created_at: datetime = Field(..., description="账户创建时间")
    updated_at: datetime = Field(..., description="账户最后更新时间")

    model_config = {
        "json_schema_extra": {
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


class Token(BaseModel):
    access_token: str = Field(..., description="JWT访问令牌")
    token_type: str = Field("bearer", description="令牌类型")


class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="用户名")
    role: Optional[str] = Field(None, description="用户角色")
