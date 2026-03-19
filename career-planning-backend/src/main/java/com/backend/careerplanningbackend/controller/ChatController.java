package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.dto.MultipartFileDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.util.AiServiceClient;
import com.backend.careerplanningbackend.util.AliOSSMultipartFileUtil;
import com.backend.careerplanningbackend.util.AliOSSUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Flux;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

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
 * @modeule ChatController
 */
@Slf4j
@RestController
@RequestMapping("/resume-upload-chat")
@RequiredArgsConstructor

public class ChatController {

    private final AiServiceClient aiServiceClient;
    private final AliOSSMultipartFileUtil aliOSSMultipartFileUtil;

    /**
     * chatWithMessage
     * 发送消息到 AI 服务（阻塞方式）
     *
     * @param message 消息内容
     * @param conversationId 对话ID（可选）
     * @param files 上传的文件（可选）
     * @return AI 响应结果
     */
    @PostMapping("/message")
    public Result chatWithMessage(
            @RequestParam(required = false) String message,
            @RequestParam(required = false) String conversationId,
            @RequestParam(required = false) MultipartFile[] files
    ) {
        log.info("收到聊天请求，message: {}, conversationId: {}, files count: {}",
                message, conversationId, files != null ? files.length : 0);

        try {
            // 处理文件上传（如果存在）
            List<String> fileUrls = new ArrayList<>();
            
            MultipartFileDTO multipartFileDTO = new MultipartFileDTO();
            if (files != null && files.length >= 0) {
                multipartFileDTO = aliOSSMultipartFileUtil.uploadFiles(files);
            }

            // 调用 AI 服务客户端，传入文件URL列表
            AiChatResponse response = aiServiceClient.chatWithMessageAndMultipartFiles("/chat/message",
                    message, multipartFileDTO.getFiles(), conversationId);

            if (response.isState()) {
                log.info("AI 响应成功，data: {}", response.getData());
                return Result.ok(response.getData());
            } else {
                log.warn("AI 响应失败，msg: {}", response.getMsg());
                return Result.fail(response.getMsg());
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
     * @param message 消息内容
     * @param conversationId 对话ID（可选）
     * @param files 上传的文件（可选）
     * @return 响应数据流
     */
    @PostMapping(value = "/message/stream", produces = "text/event-stream")
    public Flux<String> chatWithMessageStream(
            @RequestParam(required = false) String message,
            @RequestParam(required = false) String conversationId,
            @RequestParam(required = false) MultipartFile[] files
    ) {
        log.info("收到流式聊天请求，message: {}, conversationId: {}, files count: {}",
                message, conversationId, files != null ? files.length : 0);

        try {
            // 处理文件上传（如果存在）
            List<String> fileUrls = new ArrayList<>();
            
            MultipartFileDTO multipartFileDTO = new MultipartFileDTO();
            
            if (files != null && files.length > 0) {
                multipartFileDTO = aliOSSMultipartFileUtil.uploadFiles(files);
            }

            // 调用 AI 服务客户端流式接口，传入文件URL列表
            return aiServiceClient.chatWithMessageAndMultipartFilesStream("/chat/message",
                            message, multipartFileDTO.getFiles(), conversationId)
                    .doOnComplete(() -> log.info("流式响应完成"))
                    .doOnError(e -> log.error("流式响应错误", e));
        } catch (Exception e) {
            log.error("调用 AI 流式服务失败", e);
            return Flux.error(new RuntimeException("调用 AI 流式服务失败: " + e.getMessage()));
        }
    }
}
