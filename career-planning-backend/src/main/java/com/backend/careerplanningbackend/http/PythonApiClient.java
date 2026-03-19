package com.backend.careerplanningbackend.http;

import com.backend.careerplanningbackend.domain.po.Result;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;

import java.util.Map;

/**
 * Python API 客户端工具类 - 用于调用Python AI服务
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class PythonApiClient {

    private final PythonApiProperties properties;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    /** POST请求 */
    public Result post(String endpoint, Object body) {
        return post(endpoint, body, null);
    }

    /** POST请求(带自定义Header) */
    public Result post(String endpoint, Object body, Map<String, String> headers) {
        String url = buildUrl(endpoint);
        HttpEntity<Object> requestEntity = buildRequestEntity(body, headers);
        log.info("Python API POST: {}", url);
        try {
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.POST, requestEntity, String.class);
            return parseResponse(response);
        } catch (Exception e) {
            log.error("Python API 调用失败: {}", e.getMessage(), e);
            return Result.fail("AI 服务调用失败: " + e.getMessage());
        }
    }

    /** GET请求 */
    public Result get(String endpoint, Map<String, String> params) {
        return get(endpoint, params, null);
    }

    /** GET请求(带自定义Header) */
    public Result get(String endpoint, Map<String, String> params, Map<String, String> headers) {
        String url = buildUrl(endpoint, params);
        HttpEntity<?> requestEntity = buildRequestEntity(null, headers);
        log.info("Python API GET: {}", url);
        try {
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, requestEntity, String.class);
            return parseResponse(response);
        } catch (Exception e) {
            log.error("Python API 调用失败: {}", e.getMessage(), e);
            return Result.fail("AI 服务调用失败: " + e.getMessage());
        }
    }

    private String buildUrl(String endpoint) {
        String base = properties.getBaseUrl();
        if (!base.endsWith("/")) base += "/";
        return base + endpoint;
    }

    private String buildUrl(String endpoint, Map<String, String> params) {
        StringBuilder url = new StringBuilder(buildUrl(endpoint));
        if (params != null && !params.isEmpty()) {
            url.append("?");
            params.forEach((k, v) -> url.append(k).append("=").append(v).append("&"));
            url.deleteCharAt(url.length() - 1);
        }
        return url.toString();
    }

    private HttpEntity<Object> buildRequestEntity(Object body, Map<String, String> headers) {
        HttpHeaders httpHeaders = new HttpHeaders();
        httpHeaders.setContentType(MediaType.APPLICATION_JSON);
        if (properties.getApiKey() != null && !properties.getApiKey().isEmpty()) {
            httpHeaders.set("X-API-Key", properties.getApiKey());
        }
        if (headers != null) {
            headers.forEach(httpHeaders::set);
        }
        return new HttpEntity<>(body, httpHeaders);
    }

    private Result parseResponse(ResponseEntity<String> response) {
        if (response.getStatusCode().is2xxSuccessful()) {
            try {
                return objectMapper.readValue(response.getBody(), Result.class);
            } catch (Exception e) {
                return Result.ok(response.getBody());
            }
        }
        return Result.fail(response.getStatusCode().value(), "AI 服务响应异常");
    }
}
