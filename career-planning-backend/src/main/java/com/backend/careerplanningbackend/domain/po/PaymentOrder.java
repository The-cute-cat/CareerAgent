package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("payment_order")
public class PaymentOrder {

//    @TableId(type = IdType.AUTO)
    /** 订单ID，使用数据库自增 */
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    
    @NotNull(message = "套餐id")
    @TableField("package_id")
    private Integer packageId;
    
    /** 用户id */
    @TableField("user_id")
    private Long userId;
    
    private BigDecimal amount;

    /**
     * 1微信, 2支付宝
     */
    @TableField("pay_type")
    private Integer payType;
    
    private Integer points;

    private String description;
    /**
     * 0待支付, 1已支付, 2已取消, 3已退款
     */
    private Integer status;

    @TableField("pay_time")
    private LocalDateTime payTime;

    @TableField("create_time")
    private LocalDateTime createTime;

    @TableField("update_time")
    private LocalDateTime updateTime;
}