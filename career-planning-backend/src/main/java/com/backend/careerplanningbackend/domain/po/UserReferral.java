// UserReferral.java
package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("user_referral")
public class UserReferral {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long referrerId;
    private Long userId;
    private String inviteCode;
    private Integer rewardPoints;
    private Integer status;
    private LocalDateTime createTime;
    private LocalDateTime endTime;
    private LocalDateTime updateTime;
}