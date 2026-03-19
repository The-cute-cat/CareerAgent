package com.backend.careerplanningbackend.domain.dto;

import lombok.Data;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@Data
public class MultipartFileDTO {
    
    private List<MultipartFile> files;
    
    private List<String> fileNames;
}
