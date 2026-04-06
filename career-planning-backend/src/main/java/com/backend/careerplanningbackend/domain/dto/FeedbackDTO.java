package com.backend.careerplanningbackend.domain.dto;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import lombok.Data;

@Data
public class FeedbackDTO {
    private Integer id;
    private String response;
    private Integer userId;
    private String type;
    private String urlList;
    private String content;
    private String contact;
}