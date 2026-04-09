package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.po.FileUpload;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.mapper.FileUploadMapper;
import com.backend.careerplanningbackend.util.AiServiceClient;
import com.backend.careerplanningbackend.util.AliOSSUtils;
import com.backend.careerplanningbackend.util.ThreadLocalUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * ParseFileController
 * 解析文件控制器
 * 用于处理与文件解析相关的请求
 * 主要功能：
 * 1. 接收前端发送的文件上传请求
 * 2. 调用相应的服务进行文件解析
 * 3. 返回解析结果给前端
 * 4. 记录日志，便于调试和监控
 *
 */
@Slf4j
@RestController
@RequestMapping("/parse")
@RequiredArgsConstructor
public class ParseFileController {

    private final AiServiceClient aiServiceClient;
    private final AliOSSUtils aliOSSUtils;
    private final FileUploadMapper fileUploadMapper;

    /**
     * parseFile
     * 解析单个文件
     *
     * @param file 文件数据
     */
    @PostMapping("/file")
    public Result<Object> parseFile(
            @RequestParam("file") MultipartFile file,// 文件数据
            @RequestParam(value = "overwrite", defaultValue = "false") boolean overwrite //是否覆盖
    ) throws IOException {
        log.info("name: {}, size: {} bytes, leixing: {}",
                file.getOriginalFilename(), file.getSize(), file.getContentType());
        Long userId = ThreadLocalUtil.getCurrentUserId();
        String upload = aliOSSUtils.upload(file);
        FileUpload fileUpload = new FileUpload();
        fileUpload.setUserId(userId);
        fileUpload.setFileName(file.getOriginalFilename());
        fileUpload.setFileUrl(upload);
        fileUploadMapper.insert(fileUpload);

        Map<String, Object> params = new HashMap<>();
        params.put("file", file);
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOther("/parse/file", params, true);
        log.info("parse-file接收到的参数: {}", aiChatResponse.toString());
        System.out.println("python端传来的数据:" + aiChatResponse.getData());
        System.out.println("user_id:" + userId);
        System.out.println("overwrite:" + overwrite);
        System.out.println("file.getOriginalFilename():" + file.getOriginalFilename());
        System.out.println("file.getSize():" + file.getSize());
        System.out.println("file.getContentType():" + file.getContentType());
        return Result.ok(aiChatResponse.getData());
    }


    /**
     * parseFiles
     * 解析多个文件
     *
     * @param file 文件数据
     */
    @PostMapping("/files")
    public Result<Object> parseFiles(@RequestParam("file") MultipartFile file) {
        log.info("parse-resume接收到的参数: {}", file.toString());
        Map<String, Object> params = new HashMap<>();
        params.put("files", List.of(file));
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOther("/parse/files", params, true);
        log.info("parse-file接收到的参数: {}", aiChatResponse.toString());
        return Result.ok(aiChatResponse.getData());
    }
}
