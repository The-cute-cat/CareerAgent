package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.dto.CodeAbilityDTO;
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
 * CodeAbilityController
 * 代码能力评估控制器
 * 用于调用 AI 服务评估用户的代码能力
 * 主要功能：
 * 1. 接收代码仓库 URL，评估用户的代码能力
 * 2. 支持使用 AI 进行智能分析
 * 3. 返回代码能力评估结果
 * @module CodeAbilityController
 */
@Slf4j
@RestController
@RequestMapping("/codeAbility")
@RequiredArgsConstructor
public class CodeAbilityController {

    private final AiServiceClient aiServiceClient;

    /**
     * getCodeAbility
     * 评估代码能力
     *
     * @param codeAbilityDTO 代码能力评估请求参数，包含代码仓库 URL 和是否使用 AI 标志
     * @return 代码能力评估结果
     */
    @PostMapping("/evaluate")
    public Result<Object> getCodeAbility(@RequestBody CodeAbilityDTO codeAbilityDTO) {
        Map<String, Object> params = new HashMap<>();
        params.put("url", codeAbilityDTO.getUrl());
        params.put("use_ai", codeAbilityDTO.getUse_ai() != null ? codeAbilityDTO.getUse_ai() : true);
        params.put("cache_enabled", codeAbilityDTO.getCache_enabled() != null ? codeAbilityDTO.getCache_enabled() : true);
        log.info("params: {}", params);
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOtherJson("/code-ability/evaluate", params, false);
        return Result.ok(aiChatResponse.getData());

    }
    
}
