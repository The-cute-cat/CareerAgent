package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.File;
import java.util.List;

/**
 * AI 聊天请求 DTO
 * 用于封装发送给 AI 服务的请求参数
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class AiChatRequest {
    private String conversationId;
    private String message;
    private List<File> files;
}