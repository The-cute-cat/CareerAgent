from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import json

from ai_service.models.base import Base


class JobInfo(Base):
    """
        字段类型：
        id: 使用 int 类型，设置 autoincrement=True 自动递增
        短文本字段：使用 String(长度)
        长文本字段（描述）：使用 Text 类型
        时间字段：使用 DateTime 类型
        时间戳自动管理：
        created_at: 创建时自动设置为当前时间
        updated_at: 创建和更新时自动设置为当前时间
        可空性：所有字段都设置为 nullable=True，根据实际需求可以调整
        注释：使用 comment 参数添加字段说明
    """
    __tablename__ = "job_info"

    # 主键ID
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键ID")

    # 岗位信息
    job_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="岗位编码")
    job_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="岗位名称")
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="工作地址")
    salary_range: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="薪资范围")

    # 公司信息
    company_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="公司名称")
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="公司规模")
    company_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="公司类型")
    industry: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="所属行业")

    # 描述信息（使用 Text 类型以支持更长文本）
    company_desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="公司描述")
    job_desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="岗位描述")

    # 来源信息
    job_source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="岗位来源URL")

    # 时间戳
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="创建时间"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        # server_default=func.now(),
        # onupdate=func.now(),
        comment="更新时间"
    )

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
                f"created_at={self.created_at}, "
                f"updated_at={self.updated_at}"
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
