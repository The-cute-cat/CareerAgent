from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import json

from ai_service.models.base import Base


class JobInfo(Base):
    """
    岗位信息模型 - 与数据库 job_original 表结构完全对齐
    """
    __tablename__ = "job_original"

    # ==================== 主键 ====================
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )

    # ==================== 扩展字段 ====================
    job_profile_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=None,
        comment="指向合并后的岗位id，默认为空"
    )

    is_deleted: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True,
        default=0,
        comment="逻辑删除-1表示逻辑删除"
    )

    # ==================== 岗位信息 ====================
    job_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="岗位编码"
    )
    job_title: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="岗位名称"
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="工作地址"
    )
    salary_range: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="薪资范围"
    )

    # ==================== 公司信息 ====================
    company_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="公司名称"
    )
    company_size: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="公司规模"
    )
    company_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="公司类型"
    )
    industry: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="所属行业"
    )

    # ==================== 描述信息 ====================
    company_desc: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="公司描述"
    )
    job_desc: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="岗位描述"
    )

    # ==================== 来源信息 ====================
    job_source_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="岗位来源地址"
    )

    # ==================== 时间戳 ⚠️ 关键字段修正 ====================
    created_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,  # 数据库中标记为"不是null"
        comment="创建时间"
    )

    updated_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),  # 更新时自动刷新
        nullable=True,
        comment="更新日期"
    )

    # ==================== 辅助方法 ====================
    def __repr__(self) -> str:
        return (f"<JobInfo("
                f"id={self.id}, "
                f"job_code={self.job_code}, "
                f"job_title={self.job_title}, "
                f"location={self.location}, "
                f"salary_range={self.salary_range}, "
                f"company_name={self.company_name}, "
                f"company_size={self.company_size}, "
                f"company_type={self.company_type}, "
                f"industry={self.industry}, "
                f"company_desc={self.company_desc}, "
                f"job_desc={self.job_desc}, "
                f"job_source_url={self.job_source_url}, "
                f"created_time={self.created_time}, "
                f"updated_time={self.updated_time}"
                f")>")


    def to_dict(self, exclude_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        将模型实例转换为字典（可序列化为 JSON）

        Args:
            exclude_fields: 需要排除的字段列表，如 ['password', 'created_at']

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
