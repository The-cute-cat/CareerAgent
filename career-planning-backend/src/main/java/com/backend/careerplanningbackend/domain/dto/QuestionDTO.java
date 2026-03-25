package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class QuestionDTO {
    private String type;//表示想要测试的类型
    private String name;//测试技能的名称
    private String evaluationCriteria;
    private String questions;
    private String studentAnswer;
}
