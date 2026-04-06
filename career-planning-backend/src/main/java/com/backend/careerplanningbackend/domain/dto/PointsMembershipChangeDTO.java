// PointsChangeDTO.java
package com.backend.careerplanningbackend.domain.dto;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * PointsChangeDTO.java
 * 积分和会员变动DTO，用于记录用户积分和会员等级的变动信息
 */
// 和 PointsTransaction 类似，可以使用 BeanUtils.copyProperties 来简化代码
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PointsMembershipChangeDTO {
    
    @NotNull(message = "用户ID不能为空")
    private Long userId;
    
    @NotNull(message = "变动积分不能为空")
    private Integer amount; // 正数增加，负数扣减
    
    /** 1:充值, 2:购买AI报告, 3:AI知识讲解消费, 4:推广奖励, 5:系统赠送. 6:会员赠送 */
    @NotNull(message = "变动类型不能为空")
    private Integer type;

<<<<<<< HEAD

=======
>>>>>>> 515246b35b63c3a496139daa7dd8cc2ade987475
    
    /** 会员等级，0:非会员, 1:普通会员, 2:高级会员, 3:至尊会员 */
    private Integer vip;
    
    private Integer status;
    
<<<<<<< HEAD

=======
    private String description;
>>>>>>> 515246b35b63c3a496139daa7dd8cc2ade987475
}