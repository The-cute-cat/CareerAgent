package com.backend.careerplanningbackend.http;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * Python API 服务配置
 */
@Data
@Component
@ConfigurationProperties(prefix = "python-api")
public class PythonApiProperties {

    /**
     * Python 服务基础地址
     * 例如: http://localhost:8000
     */
    private String baseUrl = "http://localhost:8000";

    /**
     * 连接超时时间（毫秒）
     */
    private int connectTimeout = 30000;

    /**
     * 读取超时时间（毫秒）
     */
    private int readTimeout = 60000;

    /**
     * API 密钥（可选）
     */
    private String apiKey = "";

    /**
     * 是否启用
     */
    private boolean enabled = true;
}
