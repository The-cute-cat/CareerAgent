from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import String, DateTime, BigInteger, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import json

from ai_service.models.base import Base


class JobPortrait(Base):
    """
    岗位画像表

    字段类型：
    id: 使用 BigInteger 类型，设置 autoincrement=True 自动递增
    job_id: 使用 BigInteger 类型，关联 job_info.id
    skills_req: 使用 JSON 类型，存储岗位要求画像数据
    radar_data: 使用 JSON 类型，存储岗位雷达图基准数据
    时间戳自动管理：
    created_at: 创建时自动设置为当前时间
    updated_at: 创建和更新时自动设置为当前时间
    可空性：根据实际需求设置
    注释：使用 comment 参数添加字段说明
    """
    __tablename__ = "job_portrait"

    # 主键ID
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )

    # 关联岗位ID
    job_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="关联 job_info.id"
    )

    # 岗位要求画像 (JSON格式)
    skills_req: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="岗位要求画像(JSON)"
    )

    # 岗位雷达图基准数据 (JSON格式)
    radar_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="岗位雷达图基准数据(JSON)"
    )

    # 时间戳
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )

    # 关联关系（可选）
    # job_info: Mapped["JobInfo"] = relationship(
    #     "JobInfo",
    #     back_populates="job_portrait",
    #     foreign_keys=[job_id]
    # )

    def __repr__(self) -> str:
        return (f"<JobPortrait("
                f"id={self.id}, "
                f"job_id={self.job_id}, "
                f"skills_req={self.skills_req}, "
                f"radar_data={self.radar_data}, "
                f"created_at={self.created_at}, "
                f"updated_at={self.updated_at}"
                f")>")

    def to_dict(self, exclude_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        将模型实例转换为字典（可序列化为 JSON）

        Args:
            exclude_fields: 需要排除的字段列表，如 ['created_at', 'updated_at']

        Returns:
            dict: 可序列化为 JSON 的字典
        """
        exclude_fields = exclude_fields or []

        data = {}
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                # 处理 datetime 类型，转换为 ISO 格式字符串
                if isinstance(value, datetime):
                    value = value.isoformat()
                data[column.name] = value

        return data

    def to_json(self, exclude_fields: Optional[List[str]] = None, **json_kwargs) -> str:
        """
        将模型实例转换为 JSON 字符串

        Args:
            exclude_fields: 需要排除的字段列表
            json_kwargs: 传递给 json.dumps 的其他参数，如 indent=2

        Returns:
            str: JSON 字符串
        """
        return json.dumps(self.to_dict(exclude_fields), **json_kwargs, ensure_ascii=False)