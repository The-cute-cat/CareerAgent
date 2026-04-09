package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.util.AiServiceClient;
import com.backend.careerplanningbackend.util.ThreadLocalUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Flux;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * ChatController
 * 聊天接口控制器
 * 用于调用 AI 端（Python）的聊天功能
 * 主要功能：
 * 1. 接收前端发送的聊天消息、可选的对话 ID 和文件
 * 2. 调用 AiServiceClient 与 AI 服务进行交互
 * 3. 支持同步方式和流式方式两种聊天接口
 * 4. 支持文件上传（可选）
 * 5. 统一返回 Result 对象封装响应结果
 * 6. 记录日志，便于调试和监控
 *
 */
@Slf4j
@RestController
@RequestMapping("/chat")
@RequiredArgsConstructor

public class ChatController {

    private final AiServiceClient aiServiceClient;

    /**
     * chatWithMessage
     * 发送消息到 AI 服务（阻塞方式）
     *
     * @param message        消息内容
     * @param conversationId 对话ID（可选）
     * @param files          上传的文件（可选）
     * @return AI 响应结果
     */
    @PostMapping("/message")
    public Result<Object> chatWithMessage(
            @RequestParam("message") String message,
            @RequestParam(required = false) String conversationId,
            @RequestParam(required = false) MultipartFile[] files,
            @RequestParam(required = false) Boolean auto_extract_memory
    ) {
        try {
            Map<String, Object> params = new HashMap<>();
            params.put("message", message);
            params.put("conversation_id", conversationId == null ? UUID.randomUUID().toString() : conversationId);
            params.put("auto_extract_memory", auto_extract_memory);
            params.put("user_id", ThreadLocalUtil.getCurrentUserId().toString());
            log.info("params: {}", params);
            AiChatResponse aiChatResponse;
            if (files != null) {
                params.put("files", files);
                aiChatResponse = aiServiceClient.chatWithOther("/chat/message-and-files", params, false);
            } else {
                aiChatResponse = aiServiceClient.chatWithOther("/chat/message", params, false);
            }
            if (aiChatResponse.isState()) {
                log.info("AI 响应成功，data: {}", aiChatResponse.getData());
                return Result.ok(aiChatResponse.getData());
            } else {
                log.warn("AI 响应失败，msg: {}", aiChatResponse.getMsg());
                return Result.fail(aiChatResponse.getMsg());
            }
        } catch (Exception e) {
            log.error("调用 AI 服务失败", e);
            return Result.fail("调用 AI 服务失败: " + e.getMessage());
        }
    }

    /**
     * chatWithMessageStream
     * 发送消息到 AI 服务（流式方式）
     * 返回 SSE 流式响应
     *
     * @param message        消息内容
     * @param conversationId 对话ID（可选）
     * @param files          上传的文件（可选）
     * @return 响应数据流
     */
    @PostMapping(value = "/message/stream/message-and-files", produces = "text/event-stream")
    public Flux<String> chatWithMessageStream(
            @RequestParam("message") String message,
            @RequestParam("files") MultipartFile[] files,
            @RequestParam(required = false) String conversationId,
            @RequestParam(required = false) Boolean auto_extract_memory,
            @RequestParam(required = false) Boolean show_thinking
    ) {
        try {
            Map<String, Object> params = new HashMap<>();
            params.put("message", message);
            params.put("files", files);
            params.put("conversation_id", conversationId == null ? UUID.randomUUID().toString() : conversationId);
            params.put("auto_extract_memory", auto_extract_memory);
            params.put("show_thinking", show_thinking);
            params.put("user_id", ThreadLocalUtil.getCurrentUserId().toString());
            return aiServiceClient.chatWithOtherStream("/chat/message-and-files", params)
                    .doOnComplete(() -> log.info("消息和文件流式响应完成"))
                    .doOnError(e -> log.error("消息和文件流式响应错误", e));
        } catch (Exception e) {
            log.error("调用 AI 流式服务失败", e);
            return Flux.error(new RuntimeException("调用 AI 流式服务失败: " + e.getMessage()));
        }
    }

    @PostMapping(value = "/message/stream/message", produces = "text/event-stream")
    public Flux<String> chatWithMessageStream(
            @RequestParam("message") String message,
            @RequestParam(required = false) String conversationId,
            @RequestParam(required = false) Boolean auto_extract_memory,
            @RequestParam(required = false) Boolean show_thinking
    ) {
        try {
            Map<String, Object> params = new HashMap<>();
            params.put("message", message);
            params.put("conversation_id", conversationId == null ? UUID.randomUUID().toString() : conversationId);
            params.put("auto_extract_memory", auto_extract_memory);
            params.put("show_thinking", show_thinking);
            params.put("user_id", ThreadLocalUtil.getCurrentUserId().toString());
            return aiServiceClient.chatWithOtherStream("/chat/message/stream", params)
                    .doOnComplete(() -> log.info("仅消息流式响应完成"))
                    .doOnError(e -> log.error("仅消息流式响应错误", e));
        } catch (Exception e) {
            log.error("调用 AI 流式服务失败", e);
            return Flux.error(new RuntimeException("调用 AI 流式服务失败: " + e.getMessage()));
        }
    }


    @GetMapping("/get-chat-history")
    public Result<Object> getChatHistory(
            @RequestParam("conversation_id") String conversation_id,
            @RequestParam(required = false) Integer limit
    ) {
        Map<String, Object> params = new HashMap<>();
        params.put("user_id", ThreadLocalUtil.getCurrentUserId().toString());
        params.put("limit", limit);
        AiChatResponse aiChatResponse = aiServiceClient.getRequest("/chat/history/" + conversation_id, params, "get-chat-history", true);
        return Result.ok(aiChatResponse.getData());
    }

    @GetMapping("/get-user-sessions")
    public Result<Object> getUserSessions(
            @RequestParam(required = false) Integer page,
            @RequestParam(required = false) Integer page_size
    ) {
        Map<String, Object> params = new HashMap<>();
        params.put("user_id", ThreadLocalUtil.getCurrentUserId().toString());
        params.put("page", page);
        params.put("page_size", page_size);
        AiChatResponse aiChatResponse = aiServiceClient.getRequest("/chat/sessions", params, "get-user-sessions", true);
        return Result.ok(aiChatResponse.getData());
    }

    @GetMapping("/get-session-title")
    public Result<Object> get_session_title(
            @RequestParam("conversation_id") String conversation_id
    ) {
        Map<String, Object> params = new HashMap<>();
        params.put("user_id", ThreadLocalUtil.getCurrentUserId().toString());
        AiChatResponse aiChatResponse = aiServiceClient.getRequest("/chat/session/" + conversation_id + "/title", params, "get-session-title", true);
        return Result.ok(aiChatResponse.getData());
    }

    @DeleteMapping("/clear-session")
    public Result<Object> clear_session(
            @RequestParam("conversation_id") String conversation_id
    ) {
        Map<String, Object> params = new HashMap<>();
        params.put("user_id", ThreadLocalUtil.getCurrentUserId().toString());
        AiChatResponse aiChatResponse = aiServiceClient.deleteRequest("/chat/session/" + conversation_id, params, "clear-session", true);
        return Result.ok(aiChatResponse.getData());
    }


    @PutMapping("/update-session-title")
    public Result<Object> update_session_title(
            @RequestParam("conversation_id") String conversation_id,
            @RequestParam("title") String title
    ){
        Map<String, Object> params = new HashMap<>();
        params.put("user_id", ThreadLocalUtil.getCurrentUserId().toString());
        params.put("title", title);
        AiChatResponse aiChatResponse = aiServiceClient.putRequest("/chat/session/" + conversation_id + "/title", params, "update-session-title", true);
        return Result.ok(aiChatResponse.getData());
    }

    @GetMapping("/get-user-memories")
    public Result<Object> get_user_memories(
            @RequestParam(required = false) Integer limit,
            @RequestParam(required = false) Double min_score
    ){
        Map<String, Object> params = new HashMap<>();
        params.put("user_id", ThreadLocalUtil.getCurrentUserId().toString());
        params.put("limit", limit);
        params.put("min_score", min_score);
        AiChatResponse aiChatResponse = aiServiceClient.getRequest("/chat/memories", params, "get-user-memories", true);
        return Result.ok(aiChatResponse.getData());
    }

    @DeleteMapping("/delete-memory")
    public Result<Object> delete_memory(
            @RequestParam("memory_id") Integer memory_id
    ){
        Map<String, Object> params = new HashMap<>();
        params.put("user_id", ThreadLocalUtil.getCurrentUserId().toString());
        AiChatResponse aiChatResponse = aiServiceClient.deleteRequest("/chat/memory/" + memory_id, params, "delete-memory", true);
        return Result.ok(aiChatResponse.getData());
    }

}
