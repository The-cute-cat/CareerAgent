from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import String, DateTime, BigInteger, JSON, Text, Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import json

from ai_service.models.base import Base


class JobPortrait(Base):
    """
    岗位画像表

    对应数据库表结构：
    - 主键：id (bigint, 自增)
    - 岗位信息：job_title, tech_skills, certificates
    - 能力评分：score_innovation, score_learning, score_stress, score_communication
    - 文本描述：intern_req, potential_dir
    - 画像数据：skills_req, radar_data (JSON格式)
    - 系统字段：is_deleted, create_time, update_time
    """
    __tablename__ = "job_profile"

    # ==================== 主键 ====================
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )

    # ==================== 岗位基本信息 ====================
    job_title: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="合并后的岗位总名称"
    )

    tech_skills: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="专业技能关键词(JSON数组)"
    )

    certificates: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="证书要求"
    )

    # ==================== 能力评分 (0-100) ====================
    score_innovation: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="创新能力要求(0-100)"
    )

    score_learning: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="学习能力要求"
    )

    score_stress: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="抗压能力要求"
    )

    score_communication: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="沟通能力要求"
    )

    # ==================== 文本描述 ====================
    intern_req: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="实习经验要求"
    )

    potential_dir: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="发展潜力描述"
    )

    # ==================== 画像数据 (JSON) ====================
    skills_req: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="岗位要求画像(JSON)"
    )

    radar_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="岗位雷达图基准数据(JSON)"
    )

    # ==================== 系统字段 ====================
    is_deleted: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True,
        default=0,
        comment="逻辑删除 (0=正常, 1=删除)"
    )

    create_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=True,
        comment="创建时间"
    )

    update_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
        comment="修改时间"
    )

    # ==================== 方法 ====================
    def __repr__(self) -> str:
        return (f"<JobPortrait("
                f"id={self.id}, "
                f"job_title={self.job_title}, "
                f"tech_skills={self.tech_skills}, "
                f"create_time={self.create_time}"
                f")>")

    def to_dict(self, exclude_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        将模型实例转换为字典（可序列化为 JSON）

        Args:
            exclude_fields: 需要排除的字段列表，如 ['create_time', 'update_time']

        Returns:
            dict: 可序列化为 JSON 的字典
        """
        exclude_fields = exclude_fields or []

        data = {}
        for column in self.__table__.columns:
            if column._name not in exclude_fields:
                value = getattr(self, column._name)
                # 处理 datetime 类型，转换为 ISO 格式字符串
                if isinstance(value, datetime):
                    value = value.isoformat()
                data[column._name] = value

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

    # ==================== 辅助方法 ====================
    def get_ability_scores(self) -> Dict[str, int]:
        """
        获取四项能力评分

        Returns:
            dict: 能力评分字典
        """
        return {
            "innovation": self.score_innovation or 0,
            "learning": self.score_learning or 0,
            "stress": self.score_stress or 0,
            "communication": self.score_communication or 0
        }

    def get_radar_data(self) -> Dict[str, Any]:
        """
        获取雷达图数据（优先使用 radar_data，否则从能力评分构建）

        Returns:
            dict: 雷达图数据
        """
        if self.radar_data:
            return self.radar_data

        # 从能力评分构建默认雷达数据
        return {
            "labels": ["创新能力", "学习能力", "抗压能力", "沟通能力"],
            "values": [
                self.score_innovation or 50,
                self.score_learning or 50,
                self.score_stress or 50,
                self.score_communication or 50
            ]
        }

    def mark_deleted(self) -> None:
        """标记为逻辑删除"""
        self.is_deleted = 1

    def is_active(self) -> bool:
        """检查是否有效（未删除）"""
        return self.is_deleted != 1