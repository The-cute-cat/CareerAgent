package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ResumeData {
    private Object basic;
    private Object workExp;
    private Object skills;
    private Object data; // 可以根据实际情况定义更具体的字段
    private Object metadata; // 可以根据实际情况定义更具体的字段
}
