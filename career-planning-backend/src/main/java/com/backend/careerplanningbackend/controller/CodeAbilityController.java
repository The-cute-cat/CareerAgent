package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.dto.CodeAbilityDTO;
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
@RequestMapping("/codeAbility")
@RequiredArgsConstructor
public class CodeAbilityController {

    private final AiServiceClient aiServiceClient;
    
    @PostMapping("/evaluate")
    public Result getCodeAbility(CodeAbilityDTO codeAbilityDTO) {
        Map<String, Object> params = new HashMap<>();
        params.put("url", codeAbilityDTO.getUrl());
        params.put("use_ai", codeAbilityDTO.getUse_ai());
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOtherJson("/codeAbility/evaluate", params);
        return Result.ok(aiChatResponse.getData());
    }
    
}
