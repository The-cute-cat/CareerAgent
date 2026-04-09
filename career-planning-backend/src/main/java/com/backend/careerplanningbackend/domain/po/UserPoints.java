// UserPoints.java
package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@TableName("user_points")
public class UserPoints {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    /** 剩余积分余额 */
    private Integer pointsBalance;
    /** 该笔积分剩余可用量(用于精确扣减) */
    private Integer pointsRemainAmount;
    /** 1:有效, 0:已耗尽或已过期 */
    private Integer status;
    /** 累计消耗积分 */
    private Integer totalConsumed;
    /** 积分结束时间 */
    private LocalDateTime endTime;
    /** 活动结束时间 */
    private LocalDateTime activityEndTime;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}