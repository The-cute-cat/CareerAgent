package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.PointsChangeDTO;
import com.backend.careerplanningbackend.domain.dto.ReferralDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.service.PointsReferService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/points")
@RequiredArgsConstructor
public class PointsReferController {
    
    public final PointsReferService referralService;
    
    /**
     * getAccountPoints 获取账户积分接口
     * @param id 用户ID
     */
    @PostMapping("/account/{id}")
    public Result getAccountPoints(Long id) {
        log.info("userId: {}", id);
        return referralService.getAccountPoints(id);
    }

    /**
     * insertUserPoints 新用户赠送积分接口
     * 注册接口
     * @param referralDTO
     */
    @PostMapping("/register")
    public Result register(ReferralDTO referralDTO) {
        log.info("referralDTO: {}", referralDTO);
        return referralService.register(referralDTO);
    }
    
    /** 
     * invite
     * 邀请好友接口
     * @param referralDTO
     */
    @PostMapping("/invite")
    public Result invite(ReferralDTO referralDTO) {
        log.info("referralDTO: {}", referralDTO);
        return referralService.generateInvite(referralDTO);
    }

    /**
     * registerStudent 学生注册接口
     * 新用户赠送积分接口
     * @param referralDTO
     */
    @PostMapping("/register/student")
    public Result registerStudent(ReferralDTO referralDTO) {
        log.info("referralDTO: {}", referralDTO);
        return referralService.registerStudent(referralDTO);
    }

    /**
     * recharge 充值接口
     * 新用户赠送积分接口
     * @param dto
     */
    @PostMapping("/recharge")
    public Result recharge(@RequestBody @Valid PointsChangeDTO dto) {
        log.info("dto: {}", dto);
        return referralService.recharge(dto);
    }

    /**
     * consumePoints 消耗积分接口
     * 用户使用积分接口
     * 
     */
    @PostMapping("/consume")
    public Result consumePoints(@RequestBody @Valid PointsChangeDTO dto) {
        log.info("dto: {}", dto);
        return referralService.consumePoints(dto);
    }
    
    
    @PostMapping("/delete")
    public Result deletePoints(@RequestBody @Valid PointsChangeDTO dto) {
        log.info("dto: {}", dto);
        return referralService.deletePoints(dto); // 负数表示扣除积分
    }
}
