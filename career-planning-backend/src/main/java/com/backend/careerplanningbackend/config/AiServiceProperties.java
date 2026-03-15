package com.backend.careerplanningbackend.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * AI 服务配置属性类
 * 从 application.yaml 中读取 ai.service 前缀的配置
 */
@Data
@ConfigurationProperties(prefix = "ai.service")
@Component
public class AiServiceProperties {
    // AI 服务的基础 URL
    private String baseUrl;
    // 请求超时时间（毫秒）
    private long timeout;
    // 重试配置
    private RetryConfig retry = new RetryConfig();

    /**
     * 重试配置内部类
     */
    @Data
    public static class RetryConfig {
        // 最大重试次数，默认为 3
        private int maxAttempts = 3;
        // 重试间隔时间（毫秒），默认为 1000ms
        private long delay = 1000;
    }
}