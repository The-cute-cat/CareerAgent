package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.dto.QuestionDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.util.AiServiceClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

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
 *
 * @modeule QuestionController
 */
@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/question")
public class QuestionController {

    private final AiServiceClient aiServiceClient;

    /**
     * Generate
     * 获取生成关于某个类型的能力的问题
     *
     * @param questionDTO
     * @return
     */
    @GetMapping("/generate")
    public Result<Object> Generate(QuestionDTO questionDTO) {
        log.info("skill-generate接收到的参数: {}", questionDTO.toString());
        Map<String, Object> params = new HashMap<>();
        AiChatResponse aiChatResponse = null;

        log.debug("QuestionController.Generate 接收问题参数, 类型: {}, 名称: {}", questionDTO.getType(), questionDTO.getName());

        if ("skill".equals(questionDTO.getType())) {
            params.put("skill", questionDTO.getName());
            aiChatResponse = aiServiceClient.chatWithOther("/question/generate", params, true);
        } else if ("tool".equals(questionDTO.getType())) {
            params.put("tool", questionDTO.getName());
            aiChatResponse = aiServiceClient.chatWithOther("/question/tool_generate", params, true);
        }

        return Result.ok(aiChatResponse.getData());
    }

    /**
     * checkStudentAnswer
     * 检查问答题的答案
     *
     * @param questionDTO
     * @return
     */
    @PostMapping("/check_student_answer")
    public Result<Object> checkStudentAnswer(@RequestBody QuestionDTO questionDTO) {

        log.info("check-student-answer接收到的参数: {}", questionDTO.toString());

        Map<String, Object> params = new HashMap<>();
        params.put("questions", questionDTO.getQuestions());
        params.put("student_answer", questionDTO.getStudentAnswer());
        params.put("evaluation_criteria", questionDTO.getEvaluationCriteria());
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOther("/question/check_student_answer", params, true);
        return Result.ok(aiChatResponse.getData());
    }

}
