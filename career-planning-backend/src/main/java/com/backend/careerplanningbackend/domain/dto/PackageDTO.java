package com.backend.careerplanningbackend.domain.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * PackageDTO.java
 * 套餐数据传输对象
 * 用于前后端交互时的套餐信息传递
 * 
 * @author Career Agent
 * @version 1.0
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PackageDTO {

    private Long id;

    @NotNull(message = "套餐类型不能为空")
    private Integer type; // 1-积分套餐, 2-会员套餐

    @NotNull(message = "套餐金额不能为空")
    private BigDecimal amount;

    private Integer points; // 积分数量

    @NotBlank(message = "套餐名称不能为空")
    private String name;

    private String description;

    private Integer status; // 0-禁用，1-启用
}

