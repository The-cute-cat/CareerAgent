package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Feedback
 * 用户反馈信息PO类
 * 用于存储用户的反馈内容、邮箱、反馈类型等信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@TableName("feedback")
public class Feedback {
    
    @TableId(type = IdType.AUTO)
    private Integer id;

    private String feedbackContent;

    private String response;

    private Integer userId;

    private String email;

    private String type;
    
    private String urlList;
}