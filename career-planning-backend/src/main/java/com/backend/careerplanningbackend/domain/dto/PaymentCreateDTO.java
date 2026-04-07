package com.backend.careerplanningbackend.domain.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.math.BigDecimal;

/**
 * 创建支付订单请求
 */
@Data
public class PaymentCreateDTO {

    @NotNull(message = "支付金额不能为空")
    @Min(value = 0, message = "金额不能为负数")
    private BigDecimal amount;

    @NotNull(message = "积分数不能为空")
    @Min(value = 1, message = "积分数最少为1")
    private Integer points;

    /**
     * 支付方式: 1微信, 2支付宝
     */
    @NotNull(message = "支付方式不能为空")
    private Integer payType;

    /**
     * 套餐id
     */
    @NotNull(message = "套餐id")
    private Integer packageId;
    
    private Integer description;

    /**
     * 如果是会员购买，需要传会员等级
     */
    private Integer membershipLevel;
    
    private String name;
}