package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * Package.java
 * 套餐信息PO类
 * 用于表示系统中的各类套餐，包括积分套餐和会员套餐
 * 
 * @author Career Agent
 * @version 1.0
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@TableName("package")
public class Package {

    /** 套餐ID，使用雪花算法生成 */
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;

    /**
     * 套餐类型
     * 1-积分套餐
     * 2-会员套餐
     */
    private String type;

    /** 套餐金额 */
    private BigDecimal amount;

    /** 套餐所含积分（仅对积分套餐有效） */
    private Integer points;

    /** 套餐名称 */
    private String name;

    /** 套餐描述 */
    private String description;

    /** 是否启用：0-禁用，1-启用 */
    private Integer status;
}


