package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.PointsMembershipChangeDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.UserMembership;
import com.backend.careerplanningbackend.service.MemberService;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

// 会员接口都在这
@Slf4j
@RestController
@RequestMapping("/member")
@RequiredArgsConstructor
public class MemberController {
    
    private final MemberService memberService;

    /**
     * insertMember 新用户充值会员接口-没有被邀请过的-填过邀请码的
     * 用户注册成功后，系统会自动调用此接口为用户创建会员记录，并赠送相应的积分奖励
     * @param pointsMembershipChangeDTO
     * @return
     */
    @PostMapping("/insert")
    public Result<String> insertMember(@RequestBody PointsMembershipChangeDTO pointsMembershipChangeDTO, HttpServletResponse response) {
        log.info("pointsMembershipChangeDTO: {}", pointsMembershipChangeDTO);
        return memberService.insertMember(pointsMembershipChangeDTO,response);
    }

    /**
     * insertCodeMember 新用户会员注册接口 首次会员支付,赠送30%的积分 -没有被邀请过的-填过邀请码的
     * 用户注册成功后，系统会自动调用此接口为用户创建会员记录，并赠送相应的积分奖励
     * @param pointsMembershipChangeDTO
     * @return
     */
    @PostMapping("/insert/new")
    public Result<String> insertNewMember(@RequestBody PointsMembershipChangeDTO pointsMembershipChangeDTO) {
        log.info("pointsMembershipChangeDTO: {}", pointsMembershipChangeDTO);
        return memberService.insertCodeMember(pointsMembershipChangeDTO);
    }

    /**'
     * getMember 获取会员信息接口
     * 用户可以查询自己的会员信息，包括会员等级、到期时间等
     * @param userId
     * @return
     */
    @GetMapping("/{id}")
    public Result<UserMembership> getMember(Long userId) {
        return memberService.getMember(userId);
    }

    /**
     * updateMember 会员续费接口
     * 用户可以通过续费来延长会员有效期，系统会根据续费的时长来更新会员信息，并赠送相应的积分奖励
     * @param pointsMembershipChangeDTO
     * @return
     */
    @GetMapping("/update/{id}")
    public Result<String> updateMember(@RequestBody PointsMembershipChangeDTO pointsMembershipChangeDTO) {
        return memberService.updateMember(pointsMembershipChangeDTO);
    }
    
}
