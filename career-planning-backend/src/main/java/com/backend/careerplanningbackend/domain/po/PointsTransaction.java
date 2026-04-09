// PointsTransaction.java
package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@TableName("points_transaction")
public class PointsTransaction {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    
    @TableField("user_id")
    private Long userId;
    /** 变动前积分余额 */
    @TableField("before_amount")
    private String beforeAmount;
    
    private BigDecimal amount; // 金额变动值(正值为加，负值为减)
    
    /** 变动后积分余额 */
    @TableField("after_amount")
    private String afterAmount;
    private Integer points;  // 积分变动值(正值为加，负值为减)
    private Integer type; // 0:会员充值, 1:充值积分, 2:购买AI报告, 3:AI知识讲解消费, 4:推广奖励, 5:系统赠送
    private String description;
    @TableField("package_id")
    private Integer packageId; // 购买套餐id，非购买行为可为null
    
    @TableField("create_time")
    private LocalDateTime createTime;
    
    @TableField("update_time")
    private LocalDateTime updateTime;
    private Integer vip;
    private Integer status;
    
}