package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.dto.ConvertDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.util.AiServiceClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
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
    public Object userFormToUserProfile(@RequestBody ConvertDTO convertDTO) {
        log.info("userFormToUserProfile接收到的参数: {}", convertDTO);
        Map<String, Object> params = new HashMap<>();
        params.put("education", convertDTO.getEducation());
        params.put("major", convertDTO.getMajor());
        params.put("graduationDate", convertDTO.getGraduationDate());
        params.put("languages", convertDTO.getLanguages());
        params.put("certificates", convertDTO.getCertificates());
        params.put("skills", convertDTO.getSkills());
        params.put("tools", convertDTO.getTools());
        params.put("codeLinks", convertDTO.getCodeLinks());
        params.put("projects", convertDTO.getProjects());
        params.put("internships", convertDTO.getInternships());
        params.put("quizDetail", convertDTO.getQuizDetail());
        params.put("innovation", convertDTO.getInnovation());
        params.put("targetJob", convertDTO.getTargetJob());
        params.put("targetIndustries", convertDTO.getTargetIndustries());
        params.put("priorities", convertDTO.getPriorities());
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOtherJson("/convert/user_form_to_userprofile", params);
        Map<String, Object> params2 = new HashMap<>();
        params2.put("student_profile", aiChatResponse.getData());
        aiChatResponse = aiServiceClient.chatWithOtherJson("/matching/jobs", params2);
        return Result.ok(aiChatResponse.getData());
    }

}
