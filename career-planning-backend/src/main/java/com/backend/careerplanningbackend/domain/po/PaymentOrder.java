package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("payment_order")
public class PaymentOrder {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String orderNo;

    private Long userId;

    private BigDecimal amount;

    private Integer pointsGranted;

    /**
     * 1微信, 2支付宝
     */
    private Integer payType;

    /**
     * 0待支付, 1已支付, 2已取消, 3已退款
     */
    private Integer status;

    private String transactionId;

    private LocalDateTime payTime;

    private LocalDateTime createTime;
}