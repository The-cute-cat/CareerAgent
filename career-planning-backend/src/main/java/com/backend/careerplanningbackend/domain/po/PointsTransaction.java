// PointsTransaction.java
package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("points_transaction")
public class PointsTransaction {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private Integer amount; // 积分变动值(正值为加，负值为减)
    private Integer type; // 1:充值, 2:购买AI报告, 3:AI知识讲解消费, 4:推广奖励, 5:系统赠送
    private String description;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}