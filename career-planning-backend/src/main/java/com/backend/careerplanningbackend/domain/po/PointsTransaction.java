// PointsTransaction.java
package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
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
    private Long userId;
    private BigDecimal amount; // 金额变动值(正值为加，负值为减)
    private Integer points;  // 积分变动值(正值为加，负值为减)
    private Integer type; // 1:充值, 2:购买AI报告, 3:AI知识讲解消费, 4:推广奖励, 5:系统赠送
    private String description;
    private Integer packageId; // 购买套餐id，非购买行为可为null
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private Integer vip;
    private Integer status;
    
}