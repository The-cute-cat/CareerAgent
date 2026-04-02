package com.backend.careerplanningbackend.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;


/**
 * 支付回调请求（模拟第三方回调）
 */
@Data
public class PaymentCallbackDTO {

    @NotBlank(message = "订单号不能为空")
    private String orderNo;

    @NotBlank(message = "第三方流水号不能为空")
    private String transactionId;

    /**
     * 回调状态: SUCCESS / FAIL
     */
    @NotBlank(message = "支付结果不能为空")
    private String resultCode;
}