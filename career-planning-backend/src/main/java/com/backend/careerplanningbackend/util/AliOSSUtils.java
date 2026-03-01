package com.backend.careerplanningbackend.util;

import com.aliyun.oss.OSS;
import com.aliyun.oss.OSSClientBuilder;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;
import java.io.InputStream;
import java.util.UUID;

/**
 * 阿里云 OSS 工具类
 * 因为不属于controller层，也不属于service层，所以用component注解来存放到IOC容器里
 */
@Slf4j
@Component
public class AliOSSUtils {
    @Autowired
    private AliOSSProperties aliOSSProperties;
    /**
     * 实现上传图片到OSS
     */
    public String upload(MultipartFile file) throws IOException {
        String endpoint = aliOSSProperties.getEndpoint();
        String accessKeyId = aliOSSProperties.getAccessKeyId();
        String accessKeySecret = aliOSSProperties.getAccessKeySecret();
        String bucketName = aliOSSProperties.getBucketName();
        
        // 获取上传的文件的输入流
        InputStream inputStream = file.getInputStream();

        // 避免文件覆盖
        String originalFilename = file.getOriginalFilename();
        String fileName = UUID.randomUUID().toString() + originalFilename.substring(originalFilename.lastIndexOf("."));

        // 上传文件到 OSS
        OSS ossClient = new OSSClientBuilder().build(endpoint, accessKeyId, accessKeySecret);
        ossClient.putObject(bucketName, fileName, inputStream);

        // 文件访问路径
        String url = endpoint.split("//")[0] + "//" + bucketName + "." + endpoint.split("//")[1] + "/" + fileName;

        // 关闭ossClient
        ossClient.shutdown();
        log.info("阿里云url: {}" , url);
        System.out.println("阿里云url=" + url);
        return url; // 把上传到oss的路径返回
    }

//    private String endpoint = "https://oss-cn-hangzhou.aliyuncs.com";
//    private String accessKeyId = "{huanjingbianliang-accessKeyId}";
//    private String accessKeySecret = "{huanjingbianliang-accessKeySecret}";
//    private String bucketName = "web-tlias-study-2";
//    public String upload(String file) throws IOException {
//        // 获取上传的文件的输入流
//        InputStream inputStream = file.getInputStream();
//
//        // 避免文件覆盖
//        String originalFilename = file.getOriginalFilename();
//        String fileName = UUID.randomUUID().toString() + originalFilename.substring(originalFilename.lastIndexOf("."));
//
//        //上传文件到 OSS
//        OSS ossClient = new OSSClientBuilder().build(endpoint, accessKeyId, accessKeySecret);
//        ossClient.putObject(bucketName, fileName, inputStream);
//
//        //文件访问路径
//        String url = endpoint.split("//")[0] + "//" + bucketName + "." + endpoint.split("//")[1] + "/" + fileName;
//        // 关闭ossClient
//        ossClient.shutdown();
//        System.out.println("url="+url);
//        return url;// 把上传到oss的路径返回
//    }
}
