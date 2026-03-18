package com.backend.careerplanningbackend.util;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * FileService 将multipartFile[]转化为List<file>但是目前还有些问题,先放到这里
 * 文件服务类
 * 处理文件上传到阿里云OSS并转换为File对象列表
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class FileService {

    private final AliOSSUtils aliOSSUtils;

    /**
     * 批量上传文件到阿里云OSS并转换为File对象列表
     * 
     * @param files MultipartFile数组
     * @return File对象列表
     * @throws IOException 上传失败时抛出异常
     */
    public List<File> uploadFilesAndConvertToFileList(MultipartFile[] files) throws IOException {
        List<File> fileList = new ArrayList<>();

        if (files == null || files.length == 0) {
            log.info("没有文件需要上传");
            return fileList;
        }

        // 创建临时目录
        String tempDirPath = System.getProperty("java.io.tmpdir") + "/career-planning-temp/";
        Path tempDirPathObj = Paths.get(tempDirPath);
        if (!Files.exists(tempDirPathObj)) {
            Files.createDirectories(tempDirPathObj);
            log.info("创建临时目录: {}", tempDirPath);
        }

        // 遍历上传文件
        for (MultipartFile multipartFile : files) {
            if (multipartFile == null || multipartFile.isEmpty()) {
                continue;
            }

            try {
                // 1. 上传到阿里云OSS
                String ossUrl = aliOSSUtils.upload(multipartFile);
                log.info("文件上传到阿里云OSS成功，URL: {}", ossUrl);

                // 2. 生成临时文件名
                String originalFilename = multipartFile.getOriginalFilename();
                String fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
                String tempFileName = UUID.randomUUID().toString() + fileExtension;
                Path tempFilePath = Paths.get(tempDirPath, tempFileName);

                // 3. 将MultipartFile保存为临时File对象
                Files.copy(multipartFile.getInputStream(), tempFilePath, StandardCopyOption.REPLACE_EXISTING);
                File tempFile = tempFilePath.toFile();
                
                fileList.add(tempFile);
                log.info("临时文件创建成功: {}", tempFilePath);
                
            } catch (IOException e) {
                log.error("文件处理失败: {}", multipartFile.getOriginalFilename(), e);
                throw new IOException("文件处理失败: " + e.getMessage(), e);
            }
        }

        log.info("文件批量上传并转换完成，共处理 {} 个文件", fileList.size());
        return fileList;
    }

    /**
     * 批量上传文件到阿里云OSS并返回URL列表
     * 
     * @param files MultipartFile数组
     * @return OSS URL列表
     * @throws IOException 上传失败时抛出异常
     */
    public List<String> uploadFilesToOSS(MultipartFile[] files) throws IOException {
        List<String> fileUrls = new ArrayList<>();

        if (files == null || files.length == 0) {
            log.info("没有文件需要上传");
            return fileUrls;
        }

        // 遍历上传文件
        for (MultipartFile multipartFile : files) {
            if (multipartFile == null || multipartFile.isEmpty()) {
                continue;
            }

            try {
                // 上传到阿里云OSS
                String ossUrl = aliOSSUtils.upload(multipartFile);
                fileUrls.add(ossUrl);
                log.info("文件上传到阿里云OSS成功，URL: {}", ossUrl);
                
            } catch (IOException e) {
                log.error("文件上传失败: {}", multipartFile.getOriginalFilename(), e);
                throw new IOException("文件上传失败: " + e.getMessage(), e);
            }
        }

        log.info("文件批量上传完成，共上传 {} 个文件", fileUrls.size());
        return fileUrls;
    }

    /**
     * 删除临时文件
     * 
     * @param file 要删除的文件
     */
    public void deleteTempFile(File file) {
        if (file != null && file.exists()) {
            boolean deleted = file.delete();
            if (deleted) {
                log.info("临时文件删除成功: {}", file.getPath());
            } else {
                log.warn("临时文件删除失败: {}", file.getPath());
            }
        }
    }

    /**
     * 批量删除临时文件
     * 
     * @param files 要删除的文件列表
     */
    public void deleteTempFiles(List<File> files) {
        if (files != null && !files.isEmpty()) {
            for (File file : files) {
                deleteTempFile(file);
            }
            log.info("批量删除临时文件完成，共删除 {} 个文件", files.size());
        }
    }
}
