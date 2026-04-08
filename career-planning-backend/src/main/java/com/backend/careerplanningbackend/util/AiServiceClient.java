package com.backend.careerplanningbackend.util;

import com.backend.careerplanningbackend.config.AiServiceProperties;
import com.backend.careerplanningbackend.domain.dto.AiChatRequest;
import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;

import java.io.File;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * AI 服务客户端
 * 用于与 AI 服务进行交互，支持普通调用和流式调用
 */
@SuppressWarnings("unused")
@Slf4j
@Component
public class AiServiceClient {
    private final AiServiceProperties properties;

    private final WebClient webClient;

    /**
     * 构造函数，初始化 AI 服务客户端
     *
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
     *
     * @param url         请求的 API 路径
     * @param request     请求参数对象
     * @param enableRetry 是否启用重试机制
     * @return AI 服务响应结果
     * @throws RuntimeException 当所有重试都失败时抛出
     */
    private AiChatResponse callAiService(String url, AiChatRequest request, boolean enableRetry) {
        return universalAiService(url, buildFileBody(request), enableRetry);
    }

    /**
     * 通用 AI 服务调用方法（同步阻塞方式）
     *
     * @param url         请求的 API 路径（相对路径，会拼接 baseUrl）
     * @param builder     已构建好的多部分表单请求体
     * @param enableRetry 是否启用重试机制
     * @return AI 服务响应结果
     * @throws RuntimeException 当所有重试都失败时抛出
     */
    private AiChatResponse universalAiService(String url, MultipartBodyBuilder builder, boolean enableRetry) {
        return executeWithRetry(url, webClientBuilder -> {
            String token = AITokenUtil.createToken();
            return webClient.post()
                    .uri(properties.getBaseUrl() + url)
                    .header("Authorization", "Bearer " + token)
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(BodyInserters.fromMultipartData(builder.build()))
                    .retrieve()
                    .bodyToMono(AiChatResponse.class)
                    .timeout(Duration.ofMillis(properties.getTimeout()))
                    .block(Duration.ofMillis(properties.getTimeout()));
        }, () -> builder, "AI服务", enableRetry);
    }

    /**
     * 自定义参数对话（JSON格式，阻塞方式）
     *
     * @param url         请求的 API 路径
     * @param params      自定义参数映射
     * @param enableRetry 是否启用重试机制
     * @return AI 响应结果
     */
    public AiChatResponse chatWithOtherJson(String url, Map<String, Object> params, boolean enableRetry) {
        return executeWithRetry(url, ignored -> {
            String token = AITokenUtil.createToken();
            return webClient.post()
                    .uri(properties.getBaseUrl() + url)
                    .header("Authorization", "Bearer " + token)
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(params)
                    .retrieve()
                    .bodyToMono(AiChatResponse.class)
                    .timeout(Duration.ofMillis(properties.getTimeout()))
                    .block(Duration.ofMillis(properties.getTimeout()));
        }, () -> null, "AI服务(JSON格式)", enableRetry);
    }

    /**
     * 带重试机制的通用执行方法
     *
     * @param url             请求的 API 路径
     * @param requestExecutor 请求执行函数
     * @param bodySupplier    请求体构建函数
     * @param serviceName     服务名称（用于日志）
     * @param enableRetry     是否启用重试机制
     * @return AI 响应结果
     * @throws RuntimeException 当所有重试都失败时抛出
     */
    private AiChatResponse executeWithRetry(String url,
                                            RequestExecutor requestExecutor,
                                            BodySupplier bodySupplier,
                                            String serviceName,
                                            boolean enableRetry) {
        if (!enableRetry) {
            long startTime = System.currentTimeMillis();
            log.info("调用 {}，URL: {}", serviceName, url);
            AiChatResponse response = requestExecutor.execute(bodySupplier != null ? bodySupplier.get() : null);
            long time = System.currentTimeMillis() - startTime;
            log.info("调用{}结束，耗时：{}ms", serviceName, time);
            return response;
        }

        int tryCount = 0;
        while (tryCount < properties.getRetry().getMaxAttempts()) {
            tryCount++;
            try {
                long startTime = System.currentTimeMillis();
                log.info("调用 {}，URL: {}, 尝试次数：{}", serviceName, url, tryCount);
                AiChatResponse response = requestExecutor.execute(bodySupplier != null ? bodySupplier.get() : null);
                long time = System.currentTimeMillis() - startTime;
                log.info("调用{}结束，耗时：{}ms", serviceName, time);
                return response;
            } catch (Exception e) {
                log.warn("{}调用失败，第 {} 次尝试失败，{}", serviceName, tryCount, e.getMessage(), e);
                sleep(properties.getRetry().getDelay());
            }
        }
        throw new RuntimeException(serviceName + "调用失败，URL: " + url + ", 已达到最大重试次数");
    }

    /**
     * 请求执行函数接口
     */
    @FunctionalInterface
    private interface RequestExecutor {
        AiChatResponse execute(MultipartBodyBuilder builder);
    }

    /**
     * 请求体构建函数接口
     */
    @FunctionalInterface
    private interface BodySupplier {
        MultipartBodyBuilder get();
    }


    /**
     * 调用 AI 服务（流式响应方式）
     * 返回 Flux<String> 用于 SSE（Server-Sent Events）推送
     *
     * @param url     请求的 API 路径
     * @param request 请求参数对象
     * @return 响应数据流
     */
    private Flux<String> callAiServiceStream(String url, AiChatRequest request) {
        return universalAiServiceStream(url, buildFileBody(request));
    }

    /**
     * 通用 AI 服务流式调用方法
     * <p>
     * 返回 Flux<String> 用于 SSE（Server-Sent Events）推送，
     * 适用于需要实时响应的场景。
     *
     * @param url     请求的 API 路径（相对路径，会拼接 baseUrl）
     * @param builder 已构建好的多部分表单请求体
     * @return 响应数据流，支持背压处理
     */
    private Flux<String> universalAiServiceStream(String url, MultipartBodyBuilder builder) {
        String token = AITokenUtil.createToken();
        return webClient.post()
                .uri(properties.getBaseUrl() + url)
                .header("Authorization", "Bearer " + token)
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData(builder.build()))
                .retrieve()
                .bodyToFlux(String.class)
                .doOnError(e -> log.error("流式调用失败，URL: {}", url, e))
                .onErrorResume(e -> {
                    log.warn("流式调用出错，URL: {}, 错误信息: {}", url, e.getMessage());
                    return Flux.error(new RuntimeException("AI服务流式调用失败: " + e.getMessage(), e));
                });
    }

    private boolean isNotEmpty(String str) {
        return str != null && !str.isEmpty() && !"null".equals(str);
    }

    /**
     * 构建多部分表单请求体
     *
     * @param aiChatRequest AI 聊天请求对象
     * @return 构建好的多部分表单构建器
     */
    private MultipartBodyBuilder buildFileBody(AiChatRequest aiChatRequest) {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        // userId 是必需参数
        Optional.ofNullable(aiChatRequest.getUserId()).filter(this::isNotEmpty)
                .ifPresent(userId -> builder.part("userId", userId));
        Optional.ofNullable(aiChatRequest.getMessage()).filter(this::isNotEmpty)
                .ifPresent(message -> builder.part("message", message));
        Optional.ofNullable(aiChatRequest.getConversationId()).filter(this::isNotEmpty)
                .ifPresent(conversationId -> builder.part("conversationId", conversationId));

        // 处理文件上传
        addFilesToBuilder(builder, aiChatRequest.getFiles(), FileSystemResource::new);
        addMultipartFilesToBuilder(builder, aiChatRequest.getMultipartFiles());

        return builder;
    }

    /**
     * 添加文件到多部分表单构建器
     *
     * @param builder   多部分表单构建器
     * @param files     文件列表
     * @param converter 文件资源转换器
     * @param <T>       文件类型
     */
    private <T> void addFilesToBuilder(MultipartBodyBuilder builder, List<T> files, java.util.function.Function<T, FileSystemResource> converter) {
        if (files != null && !files.isEmpty()) {
            String partName = files.size() > 1 ? "files" : "file";
            if (files.size() > 1) {
                for (T file : files) {
                    builder.part(partName, converter.apply(file));
                }
            } else {
                builder.part(partName, converter.apply(files.getFirst()));
            }
        }
    }

    /**
     * 添加 MultipartFile 到多部分表单构建器
     *
     * @param builder        多部分表单构建器
     * @param multipartFiles MultipartFile 文件列表
     */
    private void addMultipartFilesToBuilder(MultipartBodyBuilder builder, List<MultipartFile> multipartFiles) {
        if (multipartFiles != null && !multipartFiles.isEmpty()) {
            String partName = multipartFiles.size() > 1 ? "files" : "file";
            if (multipartFiles.size() > 1) {
                for (MultipartFile file : multipartFiles) {
                    builder.part(partName, file.getResource());
                }
            } else {
                builder.part(partName, multipartFiles.getFirst().getResource());
            }
        }
    }

    /**
     * 构建自定义参数的多部分表单请求体
     * <p>
     * 用于构建非标准 AiChatRequest 格式的请求，
     * 支持任意键值对参数。
     *
     * @param params 自定义参数映射，键为参数名，值为参数值
     * @return 构建好的多部分表单构建器
     */
    private MultipartBodyBuilder buildOtherBody(Map<String, Object> params) {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        for (Map.Entry<String, Object> entry : params.entrySet()) {
            builder.part(entry.getKey(), entry.getValue());
        }
        return builder;
    }

    /**
     * 线程睡眠工具方法
     *
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
     * 纯文本消息对话（阻塞方式）
     *
     * @param url            请求的 API 路径
     * @param userId         用户 ID（必需）
     * @param message        消息内容
     * @param conversationId 对话 ID
     * @param enableRetry    是否启用重试机制
     * @return AI 响应结果
     */
    public AiChatResponse chatWithMessage(String url, String userId, String message, String conversationId, boolean enableRetry) {
        AiChatRequest request = new AiChatRequest(userId, conversationId, message);
        return callAiService(url, request, enableRetry);
    }

    /**
     * 文件上传对话（阻塞方式）
     *
     * @param url            请求的 API 路径
     * @param userId         用户 ID（必需）
     * @param files          文件列表
     * @param conversationId 对话 ID，若为空则不传递
     * @param enableRetry    是否启用重试机制
     * @return AI 响应结果
     */
    public AiChatResponse chatWithFiles(String url, String userId, List<File> files, String conversationId, boolean enableRetry) {
        AiChatRequest request = AiChatRequest.ofFiles(userId, conversationId, null, files);
        return callAiService(url, request, enableRetry);
    }

    /**
     * MultipartFile 文件上传对话（阻塞方式）
     * <p>
     * 用于处理前端直接上传的 MultipartFile 文件
     *
     * @param url            请求的 API 路径
     * @param userId         用户 ID（必需）
     * @param multipartFiles MultipartFile 文件列表
     * @param conversationId 对话 ID，若为空则不传递
     * @param enableRetry    是否启用重试机制
     * @return AI 响应结果
     */
    public AiChatResponse chatWithMultipartFiles(String url, String userId, List<MultipartFile> multipartFiles,
                                                 String conversationId, boolean enableRetry) {
        AiChatRequest request = AiChatRequest.ofMultipartFiles(userId, conversationId, null, multipartFiles);
        return callAiService(url, request, enableRetry);
    }

    /**
     * 消息和文件同时上传对话（阻塞方式）
     *
     * @param url            请求的 API 路径
     * @param userId         用户 ID（必需）
     * @param message        消息内容
     * @param files          文件列表
     * @param conversationId 对话 ID
     * @param enableRetry    是否启用重试机制
     * @return AI 响应结果
     */
    public AiChatResponse chatWithMessageAndFiles(String url, String userId, String message, List<File> files,
                                                  String conversationId, boolean enableRetry) {
        AiChatRequest request = AiChatRequest.ofFiles(userId, conversationId, message, files);
        return callAiService(url, request, enableRetry);
    }

    /**
     * 消息和 MultipartFile 文件同时上传对话（阻塞方式）
     * <p>
     * 用于处理前端直接上传的 MultipartFile 文件并附带消息
     *
     * @param url            请求的 API 路径
     * @param userId         用户 ID（必需）
     * @param message        消息内容
     * @param files          MultipartFile 文件列表
     * @param conversationId 对话 ID
     * @param enableRetry    是否启用重试机制
     * @return AI 响应结果
     */
    public AiChatResponse chatWithMessageAndMultipartFiles(String url, String userId, String message, List<MultipartFile> files,
                                                           String conversationId, boolean enableRetry) {
        AiChatRequest request = AiChatRequest.ofMultipartFiles(userId, conversationId, message, files);
        return callAiService(url, request, enableRetry);
    }

    /**
     * 自定义参数对话（阻塞方式）
     * <p>
     * 用于发送非标准格式的请求到 AI 服务，
     * 支持任意键值对参数，适用于特殊接口调用。
     *
     * @param url         请求的 API 路径
     * @param params      自定义参数映射
     * @param enableRetry 是否启用重试机制
     * @return AI 响应结果
     */
    public AiChatResponse chatWithOther(String url, Map<String, Object> params, boolean enableRetry) {
        return universalAiService(url, buildOtherBody(params), enableRetry);
    }

    /**
     * 纯文本消息对话（流式方式）
     *
     * @param url            请求的 API 路径
     * @param userId         用户 ID（必需）
     * @param message        消息内容
     * @param conversationId 对话 ID
     * @return 响应数据流
     */
    public Flux<String> chatWithMessageStream(String url, String userId, String message, String conversationId) {
        AiChatRequest request = new AiChatRequest(userId, conversationId, message);
        return callAiServiceStream(url, request);
    }

    /**
     * 文件上传对话（流式方式）
     *
     * @param url            请求的 API 路径
     * @param userId         用户 ID（必需）
     * @param files          文件列表
     * @param conversationId 对话 ID，若为空则不传递
     * @return 响应数据流
     */
    public Flux<String> chatWithFilesStream(String url, String userId, List<File> files, String conversationId) {
        AiChatRequest request = AiChatRequest.ofFiles(userId, conversationId, null, files);
        return callAiServiceStream(url, request);
    }

    /**
     * MultipartFile 文件上传对话（流式方式）
     * <p>
     * 用于处理前端直接上传的 MultipartFile 文件并接收流式响应
     *
     * @param url            请求的 API 路径
     * @param userId         用户 ID（必需）
     * @param files          MultipartFile 文件列表
     * @param conversationId 对话 ID，若为空则不传递
     * @return 响应数据流
     */
    public Flux<String> chatWithMultipartFilesStream(String url, String userId, List<MultipartFile> files, String conversationId) {
        AiChatRequest request = AiChatRequest.ofMultipartFiles(userId, conversationId, null, files);
        return callAiServiceStream(url, request);
    }

    /**
     * 消息和文件同时上传对话（流式方式）
     *
     * @param url            请求的 API 路径
     * @param userId         用户 ID（必需）
     * @param message        消息内容
     * @param files          文件列表
     * @param conversationId 对话 ID
     * @return 响应数据流
     */
    public Flux<String> chatWithMessageAndFilesStream(String url, String userId, String message, List<File> files,
                                                      String conversationId) {
        AiChatRequest request = AiChatRequest.ofFiles(userId, conversationId, message, files);
        return callAiServiceStream(url, request);
    }

    /**
     * 消息和 MultipartFile 文件同时上传对话（流式方式）
     * <p>
     * 用于处理前端直接上传的 MultipartFile 文件并附带消息，同时接收流式响应
     *
     * @param url            请求的 API 路径
     * @param userId         用户 ID（必需）
     * @param message        消息内容
     * @param files          MultipartFile 文件列表
     * @param conversationId 对话 ID
     * @return 响应数据流
     */
    public Flux<String> chatWithMessageAndMultipartFilesStream(String url, String userId, String message, List<MultipartFile> files,
                                                               String conversationId) {
        AiChatRequest request = AiChatRequest.ofMultipartFiles(userId, conversationId, message, files);
        return callAiServiceStream(url, request);
    }

    /**
     * 自定义参数对话（流式方式）
     * <p>
     * 用于发送非标准格式的请求到 AI 服务并接收流式响应，
     * 支持任意键值对参数，适用于特殊接口的实时响应场景。
     *
     * @param url    请求的 API 路径
     * @param params 自定义参数映射
     * @return 响应数据流
     */
    public Flux<String> chatWithOtherStream(String url, Map<String, Object> params) {
        return universalAiServiceStream(url, buildOtherBody(params));
    }

    /**
     * 通用 GET 请求方法
     *
     * @param url         请求的 API 路径（可包含路径参数）
     * @param queryParams 查询参数（可选）
     * @param serviceName 服务名称（用于日志）
     * @param enableRetry 是否启用重试机制
     * @return AI 响应结果
     */
    public AiChatResponse getRequest(String url, Map<String, Object> queryParams, String serviceName, boolean enableRetry) {
        return executeWithRetry(url, ignored -> {
            String token = AITokenUtil.createToken();
            WebClient.RequestHeadersSpec<?> request = webClient.get()
                    .uri(uriBuilder -> {
                        uriBuilder.path(properties.getBaseUrl() + url);
                        if (queryParams != null) {
                            queryParams.forEach((key, value) -> {
                                if (value != null) {
                                    uriBuilder.queryParam(key, value);
                                }
                            });
                        }
                        return uriBuilder.build();
                    })
                    .header("Authorization", "Bearer " + token);

            return request.retrieve()
                    .bodyToMono(AiChatResponse.class)
                    .timeout(Duration.ofMillis(properties.getTimeout()))
                    .block(Duration.ofMillis(properties.getTimeout()));
        }, () -> null, serviceName, enableRetry);
    }

    /**
     * 通用 DELETE 请求方法
     *
     * @param url         请求的 API 路径（可包含路径参数）
     * @param queryParams 查询参数（可选，如 userId）
     * @param serviceName 服务名称（用于日志）
     * @param enableRetry 是否启用重试机制
     * @return AI 响应结果
     */
    public AiChatResponse deleteRequest(String url, Map<String, Object> queryParams, String serviceName, boolean enableRetry) {
        return executeWithRetry(url, ignored -> {
            String token = AITokenUtil.createToken();
            WebClient.RequestHeadersSpec<?> request = webClient.delete()
                    .uri(uriBuilder -> {
                        uriBuilder.path(properties.getBaseUrl() + url);
                        if (queryParams != null) {
                            queryParams.forEach((key, value) -> {
                                if (value != null) {
                                    uriBuilder.queryParam(key, value);
                                }
                            });
                        }
                        return uriBuilder.build();
                    })
                    .header("Authorization", "Bearer " + token);

            return request.retrieve()
                    .bodyToMono(AiChatResponse.class)
                    .timeout(Duration.ofMillis(properties.getTimeout()))
                    .block(Duration.ofMillis(properties.getTimeout()));
        }, () -> null, serviceName, enableRetry);
    }

    /**
     * 通用 PUT 请求方法（表单格式）
     *
     * @param url         请求的 API 路径（可包含路径参数）
     * @param params      表单参数
     * @param serviceName 服务名称（用于日志）
     * @param enableRetry 是否启用重试机制
     * @return AI 响应结果
     */
    public AiChatResponse putRequest(String url, Map<String, Object> params, String serviceName, boolean enableRetry) {
        return executeWithRetry(url, ignored -> {
            String token = AITokenUtil.createToken();
            MultipartBodyBuilder builder = new MultipartBodyBuilder();
            if (params != null) {
                for (Map.Entry<String, Object> entry : params.entrySet()) {
                    builder.part(entry.getKey(), entry.getValue());
                }
            }
            return webClient.put()
                    .uri(properties.getBaseUrl() + url)
                    .header("Authorization", "Bearer " + token)
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(BodyInserters.fromMultipartData(builder.build()))
                    .retrieve()
                    .bodyToMono(AiChatResponse.class)
                    .timeout(Duration.ofMillis(properties.getTimeout()))
                    .block(Duration.ofMillis(properties.getTimeout()));
        }, () -> null, serviceName, enableRetry);
    }

}
