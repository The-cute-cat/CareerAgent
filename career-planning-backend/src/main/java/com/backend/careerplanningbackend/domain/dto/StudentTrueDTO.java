package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class StudentTrueDTO {
    private String name;
    private String schoolName;
    private String major;
    private String grade;
    private LocalDateTime entranceTime;
    private LocalDateTime graduatedTime;
}
