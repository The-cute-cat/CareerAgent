package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TransactionQueryDTO {
     private Long userId;
     
     private Integer type;
     
     private Integer amount;
     
     private String description;
     
     private Integer pageNum;
     
     private Integer pageSize;
     
     private LocalDateTime updateTime;
     
}
