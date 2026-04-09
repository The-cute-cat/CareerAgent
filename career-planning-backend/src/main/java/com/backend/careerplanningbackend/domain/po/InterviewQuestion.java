package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 八股文问答持久化实体
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@TableName("question_answer")
public class InterviewQuestion {
    private Long id;
    /** 1-选择题,2-填空题,3-场景题、架构题 */
    @TableField("select")
    private Integer selectType;
    /** 主题，如 Java 后端、数据库 */
    private String topic;
    /** 问题 */
    private String question;
    /** 答案 */
    private String answer;
    /** 数据来源：AI 或 fallback */
    private String source;
    /** 技术级别（初级/中级/高级） */
    private String stackLevel;
    /** 原始响应内容（便于排查） */
    @TableField("raw_payload")
    private String rawPayload;
    /** 中文 */
    private String language;
    /** 岗位分类 */
    @TableField("job_category")
    private Integer jobCategory;
    /** 创建时间 */
    @TableField("created_time")
    private LocalDateTime createTime;
    /** 更新时间 */
    @TableField("updated_time")
    private LocalDateTime updateTime;
}

