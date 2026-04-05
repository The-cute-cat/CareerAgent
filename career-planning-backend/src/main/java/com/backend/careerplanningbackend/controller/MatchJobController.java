package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.dto.MatchJobDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.util.AiServiceClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * MatchJobController
 * 职位匹配控制器
 * 用于根据用户画像匹配推荐合适的职位
 * 主要功能：
 * 1. 接收用户画像数据
 * 2. 调用 AI 服务进行职位匹配
 * 3. 支持配置召回和最终推荐的数量
 * 4. 返回匹配的职位列表
 * @module MatchJobController
 */
@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/matching")
public class MatchJobController {

    private final AiServiceClient aiServiceClient;

    /**
     * matchJob
     * 根据用户画像匹配职位
     *
     * @param matchJobDTO 职位匹配请求参数，包含用户画像、召回数量和最终推荐数量
     * @return 匹配的职位列表
     */
    @PostMapping("/job")
    public Result<Object> matchJob(MatchJobDTO matchJobDTO) {
        log.info("match-job接收到的参数: {}", matchJobDTO.toString());
        Map<String, Object> params = new HashMap<>();
        params.put("student_profile", matchJobDTO.getStudentProfile());
        params.put("recall_top_k", matchJobDTO.getRecallTopK());
        params.put("final_top_k", matchJobDTO.getFinalTopK());
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOther("/matching/match_job", params, true);
        return Result.ok(aiChatResponse.getData());
    }
}
