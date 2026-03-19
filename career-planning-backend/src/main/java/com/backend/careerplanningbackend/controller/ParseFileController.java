package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.util.AiServiceClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

/**
 * ParseFileController
 * 解析文件控制器
 * 用于处理与文件解析相关的请求
 * 主要功能：
 * 1. 接收前端发送的文件上传请求
 * 2. 调用相应的服务进行文件解析
 * 3. 返回解析结果给前端
 * 4. 记录日志，便于调试和监控
 * @modeule ParseFileController
 */
@Slf4j
@RestController
@RequestMapping("/parse")
@RequiredArgsConstructor
public class ParseFileController {

    private final AiServiceClient aiServiceClient;
    
    @PostMapping("/file")
    public Result<String> parseFile(@RequestParam("file") MultipartFile file) {
        log.info("parse-file接收到的参数: {}", file.toString());

        List<MultipartFile>files = new ArrayList<>();
        files.add(file);
        AiChatResponse aiChatResponse = aiServiceClient.chatWithMultipartFiles("/parse/file", files, "");
        log.info("parse-file接收到的参数: {}", aiChatResponse.toString());
        return Result.ok("aiChatResponse");
    }

    @PostMapping("/files")
    public Result<String> parseResume(@RequestParam("file") MultipartFile file) {
        log.info("parse-resume接收到的参数: {}", file.toString());

        List<MultipartFile>files = new ArrayList<>();
        files.add(file);
        AiChatResponse aiChatResponse = aiServiceClient.chatWithMultipartFiles("/parse/file", files, "");
        log.info("parse-file接收到的参数: {}", aiChatResponse.toString());
        return Result.ok("解析成功");
    }
//    @PostMapping("/file")
//    public Result<String> parseFile(@RequestParam("file") File file) {
//        log.info("parse-file接收到的参数: {}", file.toString());
//
//        List<File>files = new ArrayList<>();
//        files.add(file);
//        AiChatResponse aiChatResponse = aiServiceClient.chatWithFiles("/parse/file", files, "");
//        log.info("parse-file接收到的参数: {}", aiChatResponse.toString());
//        return Result.ok("aiChatResponse");
//    }
//
//    @PostMapping("/files")
//    public Result<String> parseResume(@RequestParam("file") File file) {
//        log.info("parse-resume接收到的参数: {}", file.toString());
//
//        List<File>files = new ArrayList<>();
//        files.add(file);
//        AiChatResponse aiChatResponse = aiServiceClient.chatWithFiles("/parse/file", files, "");
//        log.info("parse-file接收到的参数: {}", aiChatResponse.toString());
//        return Result.ok("解析成功");
//    }
}
