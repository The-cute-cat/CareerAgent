package com.backend.careerplanningbackend.domain.dto;

import lombok.Data;

@Data
public class MatchJobDTO {
    private final String studentProfile;
    private final Integer recallTopK;
    private final Integer finalTopK;
    
}
