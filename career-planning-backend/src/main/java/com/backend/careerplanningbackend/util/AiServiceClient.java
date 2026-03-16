package com.backend.careerplanningbackend.util;

import com.backend.careerplanningbackend.config.AiServiceProperties;
import com.backend.careerplanningbackend.domain.dto.AiChatRequest;
import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;

import java.io.File;
import java.time.Duration;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;


/**
 * AI 服务客户端
 * 用于与 AI 服务进行交互，支持普通调用和流式调用
 */
@Slf4j
@Component
public class AiServiceClient {
    private final AiServiceProperties properties;

    private final WebClient webClient;

    /**
     * 构造函数，初始化 AI 服务客户端
     * @param properties AI 服务配置属性
     */
    public AiServiceClient(AiServiceProperties properties) {
        this.properties = properties;
        this.webClient = WebClient.builder()
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(16 * 1024 * 1024))
                .build();
    }

    /**
     * 调用 AI 服务（同步阻塞方式）
     * 支持自动重试机制
     * @param url 请求的 API 路径
     * @param request 请求参数对象
     * @return AI 服务响应结果
     * @throws RuntimeException 当所有重试都失败时抛出
     */
    private AiChatResponse callAiService(String url, AiChatRequest request) {
        String token = AITokenUtil.createToken();
        int try_count = 0;
        // 根据配置的最大尝试次数进行重试
        while (try_count < properties.getRetry().getMaxAttempts()) {
            try {
                long startTime = System.currentTimeMillis();
                log.info("调用 AI 服务，URL: {}, 对话 ID: {}, 尝试次数：{}", url, request.getConversationId(), try_count + 1);
                AiChatResponse response = webClient.post()
                        .uri(properties.getBaseUrl() + url)
                        // 添加认证 Token
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.MULTIPART_FORM_DATA)
                        .body(BodyInserters.fromMultipartData(buildFileBody(request).build()))
                        .retrieve()
                        .bodyToMono(AiChatResponse.class)
                        // 设置超时时间
                        .timeout(Duration.ofMillis(properties.getTimeout()))
                        .block(Duration.ofMillis(properties.getTimeout()));
                // 检查响应状态
                if (response != null && response.getCode() == 200) {
                    long time = System.currentTimeMillis() - startTime;
                    log.info("调用AI服务结束，耗时：{}", time);
                    return response;
                }
            } catch (Exception e) {
                try_count++;
                log.warn("AI 服务调用失败，第 {} 次重试，{}", try_count, e.getMessage(), e);
                // 等待配置的延迟时间后重试
                sleep(properties.getRetry().getDelay());
            }
        }
        // 所有重试都失败，抛出异常
        throw new RuntimeException("AI 服务调用失败，URL: " + url + ", conversationId: " + request.getConversationId());
    }

    /**
     * 调用 AI 服务（流式响应方式）
     * 返回 Flux<String> 用于 SSE（Server-Sent Events）推送
     * @param url 请求的 API 路径
     * @param request 请求参数对象
     * @return 响应数据流
     */
    private Flux<String> callAiServiceStream(String url, AiChatRequest request) {
        AtomicReference<String> token = new AtomicReference<>(AITokenUtil.createToken());
        return webClient.post()
                .uri(properties.getBaseUrl() + url)
                .header("Authorization", "Bearer " + token.get())
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData(buildFileBody(request).build()))
                .retrieve()
                .bodyToFlux(String.class)
                .doOnError(e -> log.error("流式调用失败", e))
                .onErrorResume(e -> {
                    log.warn("流式调用出错", e);
                    return Flux.error(new RuntimeException("AI服务流式调用失败: " + e.getMessage(), e));
                });
    }

    /**
     * 构建多部分表单请求体
     * @param aiChatRequest AI 聊天请求对象
     * @return 构建好的多部分表单构建器
     */
    private MultipartBodyBuilder buildFileBody(AiChatRequest aiChatRequest) {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        if (aiChatRequest.getMessage() != null && !aiChatRequest.getMessage().isEmpty()) {
            builder.part("message", aiChatRequest.getMessage());
        }
        if (aiChatRequest.getConversationId() != null) {
            builder.part("conversationId", aiChatRequest.getConversationId());
        }
        if (aiChatRequest.getFiles() != null && !aiChatRequest.getFiles().isEmpty()) {
            for (File file : aiChatRequest.getFiles()) {
                builder.part("files", new FileSystemResource(file));
            }
        }
        return builder;
    }

    /**
     * 线程睡眠工具方法
     * @param millis 睡眠毫秒数
     */
    private void sleep(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    /**
     * 纯文本消息对话（同步方式）
     * @param url 请求的 API 路径
     * @param message 消息内容
     * @param conversationId 对话 ID
     * @return AI 响应结果
     */
    public AiChatResponse chatWithMessage(String url, String message, String conversationId) {
        AiChatRequest request = new AiChatRequest(conversationId, message, null);
        return callAiService(url, request);
    }

    /**
     * 文件上传对话（同步方式）
     * @param url 请求的 API 路径
     * @param files 文件列表
     * @param conversationId 对话 ID
     * @return AI 响应结果
     */
    public AiChatResponse chatWithFiles(String url, List<File> files, String conversationId) {
        AiChatRequest request = new AiChatRequest(conversationId, null, files);
        return callAiService(url, request);
    }

    /**
     * 消息和文件同时上传对话（同步方式）
     * @param url 请求的 API 路径
     * @param message 消息内容
     * @param files 文件列表
     * @param conversationId 对话 ID
     * @return AI 响应结果
     */
    public AiChatResponse chatWithMessageAndFiles(String url, String message, List<File> files, String conversationId) {
        AiChatRequest request = new AiChatRequest(conversationId, message, files);
        return callAiService(url, request);
    }


    /**
     * 纯文本消息对话（流式方式）
     * @param url 请求的 API 路径
     * @param message 消息内容
     * @param conversationId 对话 ID
     * @return 响应数据流
     */
    public Flux<String> chatWithMessageStream(String url, String message, String conversationId) {
        AiChatRequest request = new AiChatRequest(conversationId, message, null);
        return callAiServiceStream(url, request);
    }

    /**
     * 文件上传对话（流式方式）
     * @param url 请求的 API 路径
     * @param files 文件列表
     * @param conversationId 对话 ID
     * @return 响应数据流
     */
    public Flux<String> chatWithFilesStream(String url, List<File> files, String conversationId) {
        AiChatRequest request = new AiChatRequest(conversationId, null, files);
        return callAiServiceStream(url, request);
    }

    /**
     * 消息和文件同时上传对话（流式方式）
     * @param url 请求的 API 路径
     * @param message 消息内容
     * @param files 文件列表
     * @param conversationId 对话 ID
     * @return 响应数据流
     */
    public Flux<String> chatWithMessageAndFilesStream(String url, String message, List<File> files, String conversationId) {
        AiChatRequest request = new AiChatRequest(conversationId, message, files);
        return callAiServiceStream(url, request);
    }
}
