package com.backend.careerplanningbackend.domain.po;

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
    /** 可选：记录所属用户 */
    private Long userId;
    /** 场景题、架构题,选择题,填空题题等 */
    private Integer selectType;
    /** 主题，如 Java 后端、数据库 */
    private String topic;
    /** 技术级别 */
    private String stackLevel;
    /** 问题 */
    private String question;
    /** 答案 */
    private String answer;
    /** 数据来源：AI 或 fallback */
    private String source;
    /** 原始响应内容（便于排查） */
    private String rawPayload;
    /** 创建时间 */
    private LocalDateTime createTime;
    /** 更新时间 */
    private LocalDateTime updateTime;
}

