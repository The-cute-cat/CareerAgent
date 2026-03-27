package com.backend.careerplanningbackend.domain.vo;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户积分查询结果VO
 * 包含当前积分余额、总消费积分、最后更新时间等信息
 * 以及推广大使维度的邀请人数和推广累计获得积分
 */
@Data
public class UserPointsVO {

    private Long userId;
    private Integer pointsBalance;
    private Integer totalConsumed;
    private LocalDateTime updateTime;
    
    /** 邀请人数（推广大使维度） */
    private Integer referralCount;

    /** 推广累计获得积分 */
    private Integer referralRewardTotal;
}