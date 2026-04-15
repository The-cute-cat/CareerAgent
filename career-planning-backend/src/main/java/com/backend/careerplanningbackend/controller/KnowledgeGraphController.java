package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.util.AiServiceClient;
import com.backend.careerplanningbackend.util.ThreadLocalUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

import java.util.HashMap;
import java.util.Map;

/**
 * KnowledgeGraphController
 * 知识图谱控制器
 * 用于调用 AI 端（Python）的知识导师功能
 * 主要功能：
 * 1. 知识点岗位影响分析（流式）
 * 2. 知识点详细解释（流式）
 */
@Slf4j
@RestController
@RequestMapping("/knowledge-graph")
@RequiredArgsConstructor
public class KnowledgeGraphController {

    private final AiServiceClient aiServiceClient;

    /**
     * 流式分析知识点对岗位的影响（SSE）
     * 用于"岗位影响"标签页
     *
     * @param currentNode   当前知识点名称
     * @param jobId         目标岗位 ID
     * @param graphContext  图谱关系（可选）
     * @param industryData  行业数据（可选）
     * @return SSE 流式响应
     */
    @PostMapping(value = "/analyze/stream", produces = "text/event-stream")
    public Flux<String> analyzeKnowledgeStream(
            @RequestParam("currentNode") String currentNode,
            @RequestParam("jobId") Integer jobId,
            @RequestParam(value = "graphContext", required = false) String graphContext,
            @RequestParam(value = "industryData", required = false) String industryData
    ) {
        try {
            Long userId = ThreadLocalUtil.getCurrentUserId();
            Map<String, Object> params = new HashMap<>();
            params.put("user_id", userId);
            params.put("current_node", currentNode);
            params.put("job_id", jobId);
//            params.put("graph_context", graphContext);
//            params.put("industry_data", industryData);
            log.info("知识点岗位影响分析请求: userId={}, currentNode={}, jobId={}", userId, currentNode, jobId);
            return aiServiceClient.chatWithOtherStream("/knowledge_tutor/analyze/stream", params)
                    .doOnComplete(() -> log.info("知识点岗位影响分析流式响应完成"))
                    .doOnError(e -> log.error("知识点岗位影响分析流式响应错误", e));
        } catch (Exception e) {
            log.error("调用知识点岗位影响分析服务失败", e);
            return Flux.error(new RuntimeException("调用知识点岗位影响分析服务失败: " + e.getMessage()));
        }
    }

    /**
     * 流式解释知识点内容（SSE）
     * 用于"知识精讲"标签页
     *
     * @param currentNode   当前知识点名称
     * @param jobId         目标岗位 ID
     * @param graphContext  图谱关系（可选）
     * @return SSE 流式响应
     */
    @PostMapping(value = "/explain/stream", produces = "text/event-stream")
    public Flux<String> explainKnowledgeStream(
            @RequestParam("currentNode") String currentNode,
            @RequestParam("jobId") Integer jobId,
            @RequestParam(value = "graphContext", required = false) String graphContext
    ) {
        try {
            Long userId = ThreadLocalUtil.getCurrentUserId();
            Map<String, Object> params = new HashMap<>();
            params.put("user_id", userId);
            params.put("current_node", currentNode);
            params.put("job_id", jobId);
//            params.put("graph_context", graphContext);
            log.info("知识点解释请求: userId={}, currentNode={}, jobId={}", userId, currentNode, jobId);
            return aiServiceClient.chatWithOtherStream("/knowledge_tutor/explain/stream", params)
                    .doOnComplete(() -> log.info("知识点解释流式响应完成"))
                    .doOnError(e -> log.error("知识点解释流式响应错误", e));
        } catch (Exception e) {
            log.error("调用知识点解释服务失败", e);
            return Flux.error(new RuntimeException("调用知识点解释服务失败: " + e.getMessage()));
        }
    }
}
