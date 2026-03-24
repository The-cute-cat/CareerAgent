package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.dto.ConvertDTO;
import com.backend.careerplanningbackend.util.AiServiceClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/convert")
@Slf4j
@RequiredArgsConstructor
public class ConvertController {
    
    private final AiServiceClient aiServiceClient;
    
    @PostMapping("/user_form_to_userprofile")
    public Object userFormToUserProfile(ConvertDTO convertDTO) {
        log.info("userFormToUserProfile接收到的参数: {}", convertDTO);
        Map<String, Object> params = new HashMap<>();
        params.put("certificates", convertDTO.getCertificates());
        params.put("codeLinks", convertDTO.getCodeLinks());
        params.put("education", convertDTO.getEducation());
        params.put("graduationDate", convertDTO.getGraduationDate());
        params.put("innovation",convertDTO.getInnovation());
        params.put("internships",convertDTO.getInternships());
        params.put("languages",convertDTO.getLanguages());
        params.put("major",convertDTO.getMajor());
        params.put("priorities",convertDTO.getPriorities());
        params.put("projects",convertDTO.getProjects());
        params.put("quizScores",convertDTO.getQuizScores());
        params.put("skills", convertDTO.getSkills());
        params.put("targetIndustries", convertDTO.getTargetIndustries());
        params.put("targetJob", convertDTO.getTargetJob());
        params.put("tools", convertDTO.getTools());
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOther("/convert/user_form_to_userprofile", params);

        return aiChatResponse.getData();
    }
    
}
