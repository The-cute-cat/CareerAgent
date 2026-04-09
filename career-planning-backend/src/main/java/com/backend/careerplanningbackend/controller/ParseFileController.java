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
 *
 * @modeule ParseFileController
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
     * @param file
     * @return
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

        List<MultipartFile> files = new ArrayList<>();
        files.add(file);
        AiChatResponse aiChatResponse = aiServiceClient.chatWithMultipartFiles("/parse/file",ThreadLocalUtil.getCurrentUserId().toString() ,files, "", false);
        log.info("ParseFileController.parseFile 解析文件成功, AI返回数据: {}", aiChatResponse.getData());
        log.debug("ParseFileController.parseFile 请求参数, 用户ID: {}, 是否覆盖: {}, 文件名: {}, 文件大小: {}, 文件类型: {}",
                userId, overwrite, file.getOriginalFilename(), file.getSize(), file.getContentType());

        return Result.ok(aiChatResponse.getData());
    }


    /**
     * parseFiles
     * 解析多个文件
     *
     * @param file
     * @return
     */
    @PostMapping("/files")
    public Result<Object> parseFiles(@RequestParam("file") MultipartFile file) {
        log.info("parse-resume接收到的参数: {}", file.toString());

        List<MultipartFile> files = new ArrayList<>();
        files.add(file);
        AiChatResponse aiChatResponse = aiServiceClient.chatWithMultipartFiles("/parse/file", ThreadLocalUtil.getCurrentUserId().toString() ,files, "", false);
        log.info("parse-file接收到的参数: {}", aiChatResponse.toString());
        return Result.ok(aiChatResponse.getData());
    }
//    @PostMapping("/file")
//    public Result<AiChatResponse> parseFile(@RequestParam("file") File file) {
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
//    public Result<AiChatResponse> parseFiles(@RequestParam("file") File file) {
//        log.info("parse-resume接收到的参数: {}", file.toString());
//
//        List<File>files = new ArrayList<>();
//        files.add(file);
//        AiChatResponse aiChatResponse = aiServiceClient.chatWithFiles("/parse/file", files, "");
//        log.info("parse-file接收到的参数: {}", aiChatResponse.toString());
//        return Result.ok("解析成功");
//    }
}
