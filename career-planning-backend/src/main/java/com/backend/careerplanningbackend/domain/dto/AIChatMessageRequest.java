package com.backend.careerplanningbackend.domain.dto;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.List;

public class AIChatMessageRequest {

    private String conversationId;
    private String message;
    private String userId;
    private List<MultipartFile> multipartFiles;


    public AIChatMessageRequest(String conversationId, String message) {
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
