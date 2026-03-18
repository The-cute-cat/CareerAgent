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
    private String conversationId;
    private String message;
    private List<File> files;
    private List<MultipartFile> multipartFiles;

    public AiChatRequest(String conversationId, String message) {
        this.conversationId = conversationId;
        this.message = message;
    }


    public static AiChatRequest ofFiles(String conversationId, String message, List<File> files) {
        AiChatRequest request = new AiChatRequest(conversationId, message);
        request.setFiles(files);
        return request;
    }

    public static AiChatRequest ofMultipartFiles(String conversationId, String message, List<MultipartFile> multipartFiles) {
        AiChatRequest request = new AiChatRequest(conversationId, message);
        request.setMultipartFiles(multipartFiles);
        return request;
    }

}