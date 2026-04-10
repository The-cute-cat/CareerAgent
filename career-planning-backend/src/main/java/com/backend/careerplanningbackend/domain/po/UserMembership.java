package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("user_membership")
public class UserMembership {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    /**
     * 0普通用户, 1月度VIP, 2季度VIP, 3年度VIP, 4管理员
     */
    private Integer level;

    private LocalDateTime expireTime;

    /**
     * 0否 1是
     */
    private Integer isInfinitePoints;

    private LocalDateTime updateTime;
}