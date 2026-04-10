package com.backend.careerplanningbackend.util;

import com.backend.careerplanningbackend.domain.dto.MultipartFileDTO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

/**
 * 阿里云 OSS 工具类 多文件上传
 * 因为不属于controller层，也不属于service层，所以用component注解来存放到IOC容器里
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class AliOSSMultipartFileUtil {
    
    private final AliOSSUtils aliOSSUtil;
    
    public MultipartFileDTO uploadFiles(MultipartFile[] files) {
        if (files == null || files.length == 0) {
            log.info("没有文件需要上传");
            return null;
        }

        List<String> urlList = new ArrayList<>();
        List<String> originlList = new ArrayList<>();
        List<MultipartFile> fileList = new ArrayList<>();
        MultipartFileDTO multipartFileDTO = new MultipartFileDTO();

        for (MultipartFile multipartFile : files) {
            if (multipartFile == null || multipartFile.isEmpty()) {
                log.info("文件 {} 为空，跳过上传", multipartFile.getOriginalFilename());
                continue;
            }
            try {
                String url = aliOSSUtil.upload(multipartFile);
                log.info("文件上传到阿里云OSS成功，URL: {}", url);
                String originalFilename = multipartFile.getOriginalFilename();
                String substring = originalFilename.substring(originalFilename.lastIndexOf("."));
                // todo 这里需要把用户的源文件名字改回用户上传的文字
                log.debug("AliOSSMultipartFileUtil.uploadFiles 文件截取结果, substring: {}, originalFilename: {}", substring, originalFilename);

                originlList.add(substring);
                urlList.add(url);

                fileList.add(multipartFile);
            } catch (Exception e) {
                log.error("文件上传失败", e);
            }
        }

        multipartFileDTO.setFileNames(urlList);
        multipartFileDTO.setFiles(fileList);
        return multipartFileDTO;
    }
}
