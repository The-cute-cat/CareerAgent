package com.backend.careerplanningbackend.domain.dto;

import lombok.Data;

@Data
public class FeedbackDTO {
    private Integer id;
    private String feedbackContent;
    private String response;
    private Integer userId;
    private String email;
    private String type;
    private String urlList;
}