package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.PointsMembershipChangeDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.UserMembership;
import com.backend.careerplanningbackend.service.MemberService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/member")
@RequiredArgsConstructor
public class MemberController {
    
    private final MemberService memberService;
    
    @PostMapping("/insert")
    public Result<String> insertMember(@RequestBody PointsMembershipChangeDTO pointsMembershipChangeDTO) {
        log.info("pointsMembershipChangeDTO: {}", pointsMembershipChangeDTO);
        return memberService.insertMember(pointsMembershipChangeDTO);
    }

    @PostMapping("/insert/new")
    public Result<String> insertNewMember(@RequestBody PointsMembershipChangeDTO pointsMembershipChangeDTO) {
        log.info("pointsMembershipChangeDTO: {}", pointsMembershipChangeDTO);
        return memberService.insertNewMember(pointsMembershipChangeDTO);
    }

    @GetMapping("/{id}")
    public Result<UserMembership> getMember(Long userId) {
        return memberService.getMember(userId);
    }

    @GetMapping("/update/{id}")
    public Result<String> updateMember(@RequestBody PointsMembershipChangeDTO pointsMembershipChangeDTO) {
        return memberService.updateMember(pointsMembershipChangeDTO);
    }
    
}
