// PointsChangeDTO.java
package com.backend.careerplanningbackend.domain.dto;

//import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

/**
 * 积分充值消费邀请等等
 * 
 */
@Data
public class PointsChangeDTO {
    @NotNull(message = "用户ID不能为空")
    private Long userId;
    
    @NotNull(message = "变动积分不能为空")
    private Integer amount; // 正数增加，负数扣减
    
    @NotNull(message = "变动类型不能为空")
    private Integer type;
    
    private String description;
}