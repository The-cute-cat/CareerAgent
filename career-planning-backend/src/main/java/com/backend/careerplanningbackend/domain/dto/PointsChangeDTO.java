// PointsChangeDTO.java
package com.backend.careerplanningbackend.domain.dto;

//import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 积分充值消费邀请等等
 * 
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PointsChangeDTO {
    @NotNull(message = "用户ID不能为空")
    private Long userId;
    
    @NotNull(message = "变动积分不能为空")
    private Integer amount; // 正数增加，负数扣减
    
    /** 1:充值, 2:购买AI报告, 3:AI知识讲解消费, 4:推广奖励, 5:系统赠送 */
    @NotNull(message = "变动类型不能为空")
    private Integer type;

    private String description;
}