from typing import Any

from pydantic import BaseModel, Field


class ReportCheckRequest(BaseModel):
    """报告完整性检查请求"""
    user_id: int = Field(..., description="用户ID（用于自动查询用户画像）")
    report_content: str = Field(..., description="报告文本内容")
    job_title: str | None = Field(None, description="目标岗位名称")


class CheckResult(BaseModel):
    """单个维度的检查结果"""
    dimension: str = Field(..., description="维度名称")
    is_present: bool = Field(..., description="是否存在")
    description: str = Field(..., description="检查说明")
    suggestion: str | None = Field(None, description="改进建议")


class ReportCheckResponse(BaseModel):
    """报告完整性检查响应"""
    is_complete: bool = Field(..., description="报告是否完整")
    check_results: list[CheckResult] = Field(default_factory=list, description="各维度检查详情")
    missing_items: list[str] = Field(default_factory=list, description="缺失项列表")
    overall_score: int = Field(..., description="总体评分（0-100）")
    summary: str = Field(..., description="整体评价和建议")


class ParagraphPolishRequest(BaseModel):
    """段落润色请求"""
    original_content: str = Field(..., description="原始文本内容")
    report_type: str = Field(..., description="报告类型：match_analysis（匹配分析）、action_plan（行动计划）、other（其他）")
    context: dict[str, Any] | None = Field(None, description="上下文信息（如岗位名称、用户信息等）")


class ParagraphPolishResponse(BaseModel):
    """段落润色响应"""
    original_content: str = Field(..., description="原始内容")
    polished_content: str = Field(..., description="润色后内容")
    report_type: str = Field(..., description="报告类型")
    length_before: int = Field(..., description="润色前长度")
    length_after: int = Field(..., description="润色后长度")
