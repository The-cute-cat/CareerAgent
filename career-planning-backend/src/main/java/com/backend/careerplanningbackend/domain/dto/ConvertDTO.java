package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Date;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class ConvertDTO {
    private String education;
    private String major;
    private String graduationDate;
    private Language[] languages;
    private String[] certificates;
    private SkillTool[] skills;
    private SkillTool[] tools;
    private String[] codeLinks = null;
    private Project[] projects;
    private Internship[] internships;
    private QuizDetailItem[] quizDetail = null;
    private String innovation;
    private String targetJob;
    private String[] targetIndustries;
    private String[] priorities;

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    private static class Language {
        private String type;
        private String level;
        private String other;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    private static class SkillTool {
        private String name;
        private int score;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    private static class Project {
        private boolean isCompetition;
        private String name;
        private String desc;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    private static class Internship {
        private String company;
        private String role;
        private String[] date;
        private String desc;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    private static class QuizDetailItem {
        private String type;
        private String question;
        private String answer;
    }
}
