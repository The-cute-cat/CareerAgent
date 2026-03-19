package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.dto.QuestionDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.util.AiServiceClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * QuestionController
 * 问题接口控制器
 * 用于处理与问题相关的请求
 * 主要功能：
 * 1. 接收前端发送的与问题相关的请求
 * 2. 调用 AiServiceClient 与 AI 服务进行交互，获取问题相关的结果
 * 3. 返回结果给前端
 * 4. 记录日志，便于调试和监控
 * @modeule QuestionController
 */
@Slf4j
@RestController
@RequiredArgsConstructor
public class QuestionController {
    
    private final AiServiceClient aiServiceClient;

    /**
     * skillGenerate
     * 获取生成关于某个技能的问题
     * 
     * @param questionDTO
     * @return
     */
    @PostMapping("/test_question/skill_generate")
    public Result<Object> skillGenerate(QuestionDTO questionDTO) {
        log.info("skill-generate接收到的参数: {}", questionDTO.toString());
        Map<String, Object> params = new HashMap<>();
        params.put("skill", questionDTO.getSkill());
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOther("/test_question/skill_generate", params);
        return Result.ok(aiChatResponse.getData());
    }

    /**
     * toolGenerate
     * 获取生成关于某个工具的问题
     * 
     * @param questionDTO
     * @return
     */
    @PostMapping("/test_question/tool_generate")
    public Result<Object> toolGenerate(QuestionDTO questionDTO) {
        log.info("tool-generate接收到的参数: {}", questionDTO.toString());
        Map<String, Object> params = new HashMap<>();
        params.put("tool", questionDTO.getTool());
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOther("/test_question/tool_generate", params);
        return Result.ok(aiChatResponse.getData());
    }

    /**
     * checkStudentAnswer
     * 检查问答题的答案
     * 
     * @param questionDTO
     * @return
     */
    @PostMapping("/test_question/check_student_answer")
    public Result<Object> checkStudentAnswer(QuestionDTO questionDTO) {
        log.info("check-student-answer接收到的参数: {}", questionDTO.toString());
        Map<String, Object> params = new HashMap<>();
        params.put("questions", questionDTO.getQuestions());
        params.put("student_answer", questionDTO.getStudentAnswer());
        params.put("evaluation_criteria", questionDTO.getEvaluationCriteria());
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOther("/test_question/check_student_answer", params);
        return Result.ok(aiChatResponse.getData());
    }
    
}
