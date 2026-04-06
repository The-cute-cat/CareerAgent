package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.PointsMembershipChangeDTO;
import com.backend.careerplanningbackend.domain.dto.ReferralDTO;
import com.backend.careerplanningbackend.domain.dto.StudentTrueDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.UserPoints;
import com.backend.careerplanningbackend.domain.vo.UserPointsVO;
import com.backend.careerplanningbackend.service.PointsReferService;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

/**
 * PointsReferController
 * 负责处理积分相关的请求，如获取账户积分、注册赠送积分、邀请好友等
 * 1. 获取账户积分接口：用户可以查询自己的当前积分余额
 * 2. 注册赠送积分接口：新用户注册成功后，系统会自动赠送一定数量的积分
 * 3. 邀请好友接口：用户可以通过邀请好友注册来获得额外的积分奖励
 * 4. 学生注册接口：学生用户注册成功后，系统会自动赠送一定数量的积分
 * 5. 充值接口：用户可以通过充值来增加自己的积分余额
 * 6. 消耗积分接口：用户在购买课程或服务时可以使用积分抵扣部分金额，消耗相应的积分
 * @module PointsReferController
 */
// 积分接口都在这
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
    public Result<UserPointsVO> getAccountPoints(@PathVariable("id") Long id) {
        log.info("userId: {}", id);
        return referralService.getAccountPoints(id);
    }

    /**
     * register
     * 新用户注册赠送积分接口
     * 用户注册成功后，系统会自动赠送一定数量的积分
     *
     * @param referralDTO 注册信息，包含邀请码等
     * @return 注册结果
     */
    @PostMapping("/register")
    public Result<Object> register(ReferralDTO referralDTO) {
        log.info("referralDTO: {}", referralDTO);
        return referralService.register(referralDTO);
    }
    
    /**
     * invite
     * 邀请好友接口
     * 用户可以通过邀请好友注册来获得额外的积分奖励
     *
     * @param referralDTO 邀请信息
     * @return 邀请码信息
     */
    @PostMapping("/invite")
    public Result<ReferralDTO> invite(ReferralDTO referralDTO) {
        log.info("referralDTO: {}", referralDTO);
        return referralService.generateInvite(referralDTO);
    }

    /**
     * registerStudent
     * 大学生认证接口
     * 学生用户认证成功后，系统会自动赠送一定数量的积分
     *
     * @param studentTrueDTO 学生认证信息
     * @return 认证结果
     */
    @PostMapping("/register/student")
    public Result<Object> registerStudent(StudentTrueDTO studentTrueDTO) {
        log.info("studentTrueDTO: {}", studentTrueDTO);
        return referralService.registerStudent(studentTrueDTO);
    }

    /**
     * recharge
     * 充值积分接口
     * 用户可以通过充值来增加自己的积分余额
     *
     * @param dto 充值信息
     * @param response HTTP 响应对象
     * @return 充值后的积分信息
     */
    @PostMapping("/recharge")
    public Result<UserPoints> recharge(@RequestBody @Valid PointsMembershipChangeDTO dto, HttpServletResponse response) {
        log.info("dto: {}", dto);
        return referralService.recharge(dto,response);
    }

    /**
     * consumePoints
     * 消耗积分接口
     * 用户在购买课程或服务时可以使用积分抵扣部分金额，消耗相应的积分
     *
     * @param dto 积分消耗信息
     * @return 消耗后的积分信息
     */
    @PostMapping("/consume")
    public Result<UserPoints> consumePoints(@RequestBody @Valid PointsMembershipChangeDTO dto) {
        log.info("dto: {}", dto);
        return referralService.consumePoints(dto);
    }
    
    
    /**
     * deletePoints
     * 删除积分接口
     * 用于扣除用户积分，传入负数表示扣除积分
     *
     * @param dto 积分变更信息
     * @return 操作结果
     */
    @PostMapping("/delete")
    public Result<Object> deletePoints(@RequestBody @Valid PointsMembershipChangeDTO dto) {
        log.info("dto: {}", dto);
        return referralService.deletePoints(dto); // 负数表示扣除积分
    }
}
