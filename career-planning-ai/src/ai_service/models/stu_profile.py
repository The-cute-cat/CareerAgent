from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import String, DateTime, BigInteger, JSON, Text, Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import json

from ai_service.models.base import Base


class StuProfile(Base):
    """
    学生画像/能力表

    对应数据库表结构：
    - 主键：id (bigint, 自增)
    - 关联信息：stu_id
    - JSON数据：people_form, people_profile, tech_skills, radar_data, soft_skills, skills_stu
    - 能力评分：score_innovation, score_learning, score_stress, score_communication, score_integrity, score_compete
    - 文本描述：intern_exp
    - 系统字段：is_deleted, create_time, update_time
    """
    __tablename__ = "stu_profile"

    # ==================== 主键与外键 ====================
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="主键ID/学生能力表"
    )

    stu_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="关联stu_info ID"
    )

    # ==================== 基础画像与技能 (JSON) ====================
    people_form: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="人物表单信息"
    )

    people_profile: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="人物画像信息"
    )

    tech_skills: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="掌握技能专业技能(JSON数组，如 [\"Java\", \"Spring\"])"
    )

    soft_skills: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="软素质评估 (JSON对象，包含创新、抗压、沟通的打分)"
    )

    radar_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="雷达图维度分数数据 (JSON)"
    )

    skills_stu: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="人物画像总"
    )

    # ==================== 能力与综合评分 ====================
    score_innovation: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="创新能力评分"
    )

    score_learning: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="学习能力评分"
    )

    score_stress: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="抗压能力评分"
    )

    score_communication: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="沟通能力评分"
    )

    score_integrity: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="画像完整度评分"
    )

    score_compete: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="就业竞争力评分"
    )

    # ==================== 文本描述 ====================
    intern_exp: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="实习/项目经历"
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
        return (f"<StuProfile("
                f"id={self.id}, "
                f"stu_id={self.stu_id}, "
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

    # ==================== 辅助方法 ====================
    def get_ability_scores(self) -> Dict[str, int]:
        """
        获取四项基础能力评分

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