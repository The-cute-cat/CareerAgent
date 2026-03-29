package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class MatchJobDTO {
    private String studentProfile;
    private Integer recallTopK;
    private Integer finalTopK;
    
}
