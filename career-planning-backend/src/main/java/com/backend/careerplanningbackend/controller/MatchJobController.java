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

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/matching")
public class MatchJobController {

    private final AiServiceClient aiServiceClient;
    
    @PostMapping("/job")
    public Result<Object> matchJob(MatchJobDTO matchJobDTO) {
        log.info("match-job接收到的参数: {}", matchJobDTO.toString());
        Map<String, Object> params = new HashMap<>();
        params.put("student_profile", matchJobDTO.getStudentProfile());
        params.put("recall_top_k", matchJobDTO.getRecallTopK());
        params.put("final_top_k", matchJobDTO.getFinalTopK());
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOther("/matching/match_job", params);
        return Result.ok(aiChatResponse.getData());
    }
}
