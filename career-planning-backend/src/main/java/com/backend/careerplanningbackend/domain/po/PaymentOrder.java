package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
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
    @TableId(type = IdType.ASSIGN_ID)
    /** 订单ID，使用数据库自增 */
    private Long id;

    /**
     * 订单id
     */
    @NotNull(message = "订单id")
    private Integer packageId;
    
    private Integer amount;

    /**
     * 1微信, 2支付宝
     */
    private Integer payType;
    
    private Integer points;

    /**
     * 0待支付, 1已支付, 2已取消, 3已退款
     */
    private Integer status;

    private LocalDateTime payTime;

    private LocalDateTime createTime;
}