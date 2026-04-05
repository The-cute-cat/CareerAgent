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

/**
 * ConvertController
 * 数据转换控制器
 * 用于将用户表单数据转换为用户画像数据，并进行职位匹配
 * 主要功能：
 * 1. 接收前端提交的用户表单数据（教育、技能、项目等信息）
 * 2. 调用 AI 服务将表单数据转换为结构化的用户画像
 * 3. 基于用户画像进行职位匹配推荐
 * 4. 返回匹配的职位列表
 * @module ConvertController
 */
@RestController
@RequestMapping("/convert")
@Slf4j
@RequiredArgsConstructor
public class ConvertController {

    private final AiServiceClient aiServiceClient;

    /**
     * userFormToUserProfile
     * 将用户表单数据转换为用户画像并匹配职位
     *
     * @param convertDTO 用户表单数据，包含教育背景、专业技能、项目经历、实习经历等信息
     * @return 匹配的职位列表
     */
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
