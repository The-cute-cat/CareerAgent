package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class QuestionDTO {
    private String skill;
    private String tool;
    private String evaluationCriteria;
    private String questions;
    private String studentAnswer;
}
