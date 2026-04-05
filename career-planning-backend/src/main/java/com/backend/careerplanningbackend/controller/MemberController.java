package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.PointsMembershipChangeDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.UserMembership;
import com.backend.careerplanningbackend.service.MemberService;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

/**
 * MemberController
 * 会员管理控制器
 * 处理会员相关的业务逻辑，包括会员注册、续费、信息查询等
 * 主要功能：
 * 1. 新用户充值会员注册，并赠送积分奖励
 * 2. 新用户首次会员支付，赠送 30% 积分
 * 3. 会员信息查询
 * 4. 会员续费
 * @module MemberController
 */
// 会员接口都在这
@Slf4j
@RestController
@RequestMapping("/member")
@RequiredArgsConstructor
public class MemberController {

    private final MemberService memberService;

    /**
     * insertMember
     * 新用户充值会员注册接口
     * 用户注册成功后，系统会自动调用此接口为用户创建会员记录，并赠送相应的积分奖励
     * 适用于：没有被邀请过、但填写过邀请码的用户
     *
     * @param pointsMembershipChangeDTO 会员变更信息
     * @param response HTTP 响应对象
     * @return 操作结果
     */
    @PostMapping("/insert")
    public Result<String> insertMember(@RequestBody PointsMembershipChangeDTO pointsMembershipChangeDTO, HttpServletResponse response) {
        log.info("pointsMembershipChangeDTO: {}", pointsMembershipChangeDTO);
        return memberService.insertMember(pointsMembershipChangeDTO,response);
    }

    /**
     * insertNewMember
     * 新用户会员注册接口
     * 首次会员支付，赠送 30% 的积分
     * 适用于：没有被邀请过、但填写过邀请码的用户
     *
     * @param pointsMembershipChangeDTO 会员变更信息
     * @return 操作结果
     */
    @PostMapping("/insert/new")
    public Result<String> insertNewMember(@RequestBody PointsMembershipChangeDTO pointsMembershipChangeDTO) {
        log.info("pointsMembershipChangeDTO: {}", pointsMembershipChangeDTO);
        return memberService.insertCodeMember(pointsMembershipChangeDTO);
    }

    /**
     * getMember
     * 获取会员信息接口
     * 用户可以查询自己的会员信息，包括会员等级、到期时间等
     *
     * @param userId 用户 ID
     * @return 会员信息
     */
    @GetMapping("/{id}")
    public Result<UserMembership> getMember(Long userId) {
        return memberService.getMember(userId);
    }

    /**
     * updateMember
     * 会员续费接口
     * 用户可以通过续费来延长会员有效期，系统会根据续费的时长来更新会员信息，并赠送相应的积分奖励
     *
     * @param pointsMembershipChangeDTO 会员变更信息
     * @return 操作结果
     */
    @GetMapping("/update/{id}")
    public Result<String> updateMember(@RequestBody PointsMembershipChangeDTO pointsMembershipChangeDTO) {
        return memberService.updateMember(pointsMembershipChangeDTO);
    }
    
}
