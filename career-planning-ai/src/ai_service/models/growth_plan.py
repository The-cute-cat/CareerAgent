"""
成长计划数据模型

设计原则：
1. AI 只返回资源引用 (ID + 类型)
2. 后续通过 get_resources_by_ids 查询完整信息
3. 前端展示时再查库获取准确数据
"""
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class ResourceType(str, Enum):
    """资源类型"""
    BOOK = "book"
    VIDEO = "video"
    PROJECT = "project"
    INTERN = "intern"

class ResourceRef(BaseModel):
    """资源引用 - 用于 AI 输出，后续通过 ID 查询完整信息"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(description="资源唯一ID，来自工具返回的 id 字段")
    type: ResourceType = Field(description="资源类型：book/video/project/intern")
    name: str = Field(description="资源名称/标题，用于展示")
    reason: str = Field(description="推荐理由，简短说明为什么推荐这个资源")

class TaskPriority(str, Enum):
    """任务优先级"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class LearningTask(BaseModel):
    """学习任务"""
    model_config = ConfigDict(populate_by_name=True)
    
    task_name: str = Field(description="任务名称，如'学习 Spring Boot 基础'")
    description: str = Field(description="具体要做什么，如何做")
    priority: TaskPriority = Field(description="优先级：高/中/低")
    estimated_time: str = Field(description="预计耗时，如'2周'、'1个月'")
    skill_target: str = Field(description="该任务要提升的技能点")
    success_criteria: str = Field(description="如何判断任务完成")
    resources: List[ResourceRef] = Field(
        default_factory=list,
        description="推荐的资源引用列表，包含 id、type、name、reason"
    )


class Milestone(BaseModel):
    """里程碑"""
    model_config = ConfigDict(populate_by_name=True)
    
    milestone_name: str = Field(description="里程碑名称，如'完成 Java 基础阶段'")
    target_date: str = Field(description="目标时间，如'第1个月末'")
    key_results: List[str] = Field(description="该里程碑需要达成的关键成果列表")
    tasks: List[LearningTask] = Field(description="该里程碑包含的任务列表")


# ============================================
# 短期和中期计划
# ============================================

class ShortTermPlan(BaseModel):
    """短期计划 (1-3个月)"""
    model_config = ConfigDict(populate_by_name=True)
    
    duration: str = Field(description="周期，如'1-3个月'")
    goal: str = Field(description="短期核心目标")
    focus_areas: List[str] = Field(description="需要重点提升的技能领域")
    milestones: List[Milestone] = Field(description="关键里程碑")
    quick_wins: List[str] = Field(
        default_factory=list,
        description="短期内可快速达成的成果，增强信心"
    )


class MidTermPlan(BaseModel):
    """中期计划 (3-12个月)"""
    model_config = ConfigDict(populate_by_name=True)
    
    duration: str = Field(description="周期，如'3-12个月'")
    goal: str = Field(description="中期核心目标")
    skill_roadmap: List[str] = Field(description="技能提升路径")
    milestones: List[Milestone] = Field(description="关键里程碑")
    career_progression: str = Field(description="预期达到的职业水平或可胜任的岗位")
    recommended_internships: List[ResourceRef] = Field(
        default_factory=list,
        description="推荐的实习机会引用"
    )


# ============================================
# 成长计划总模型
# ============================================

class GrowthPlan(BaseModel):
    """
    成长计划总模型
    
    注意：所有资源引用只包含 ID 和类型，
    前端展示时需调用 get_resources_by_ids 获取完整信息
    """
    model_config = ConfigDict(populate_by_name=True)
    
    student_summary: str = Field(description="学生背景和现状概述")
    target_position: str = Field(description="目标岗位名称")
    target_position_profile_summary: str = Field(description="目标岗位画像摘要")
    current_gap: str = Field(description="当前与目标的主要差距")
    
    short_term_plan: ShortTermPlan = Field(description="短期计划 (1-3个月)")
    mid_term_plan: MidTermPlan = Field(description="中期计划 (3-12个月)")
    
    action_checklist: List[str] = Field(
        default_factory=list,
        description="本周就可以开始做的具体行动项"
    )
    
    tips: List[str] = Field(
        default_factory=list,
        description="给学生的职业发展建议"
    )

    def get_all_resource_refs(self) -> List[ResourceRef]:
        """获取所有资源引用，用于批量查询"""
        refs = []
        
        # 从短期计划收集
        for milestone in self.short_term_plan.milestones:
            for task in milestone.tasks:
                refs.extend(task.resources)
        
        # 从中期计划收集
        for milestone in self.mid_term_plan.milestones:
            for task in milestone.tasks:
                refs.extend(task.resources)
        refs.extend(self.mid_term_plan.recommended_internships)
        
        return refs
