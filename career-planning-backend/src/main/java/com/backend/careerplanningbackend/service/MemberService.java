package com.backend.careerplanningbackend.service;

import com.backend.careerplanningbackend.domain.dto.PointsMembershipChangeDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.UserMembership;

public interface MemberService {
    
    Result<String> insertMember(PointsMembershipChangeDTO pointsMembershipChangeDTO);

    Result<String> insertNewMember(PointsMembershipChangeDTO pointsMembershipChangeDTO);

    Result<UserMembership> getMember(Long userId);

    Result<String> updateMember(PointsMembershipChangeDTO pointsMembershipChangeDTO);
}
