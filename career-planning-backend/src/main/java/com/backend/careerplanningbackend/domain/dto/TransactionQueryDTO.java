package com.backend.careerplanningbackend.domain.dto;

import java.time.LocalDateTime;

public class TransactionQueryDTO {
     private Long userId;
     
     private Integer type;
     
     private Integer amount;
     
     private String description;
     
     private Integer pageNum;
     
     private Integer pageSize;
     
     private LocalDateTime updateTime;
     
}
