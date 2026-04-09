package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.web.multipart.MultipartFile;

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
    private Long userId;
    private String conversationId;
    private String message;
    private List<File> files;
    private List<MultipartFile> multipartFiles;

    public AiChatRequest(Long userId, String conversationId, String message) {
        this.userId = userId;
        this.conversationId = conversationId;
        this.message = message;
    }


    public static AiChatRequest ofFiles(Long userId, String conversationId, String message, List<File> files) {
        AiChatRequest request = new AiChatRequest(userId, conversationId, message);
        request.setFiles(files);
        return request;
    }

    public static AiChatRequest ofMultipartFiles(Long userId, String conversationId, String message, List<MultipartFile> multipartFiles) {
        AiChatRequest request = new AiChatRequest(userId, conversationId, message);
        request.setMultipartFiles(multipartFiles);
        return request;
    }

}