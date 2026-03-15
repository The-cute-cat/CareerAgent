package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * AI 聊天响应 DTO
 * 用于封装 AI 服务返回的响应数据
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class AiChatResponse {
    // 响应状态码（200 表示成功）
    private int code;
    // 请求是否成功
    private boolean state;
    // 响应消息
    private String msg;
    // 响应数据（根据不同接口返回不同类型）
    private Object data;
}