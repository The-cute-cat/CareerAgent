package com.backend.careerplanningbackend.service;

import com.backend.careerplanningbackend.domain.dto.PointsMembershipChangeDTO;
import com.backend.careerplanningbackend.domain.dto.ReferralDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import jakarta.validation.Valid;

public interface PointsReferService {


    Result getAccountPoints(Long userId);

    Result register(ReferralDTO referralDTO);

    Result generateInvite(ReferralDTO referralDTO);
    
    Result registerStudent(ReferralDTO referralDTO);

    Result recharge(@Valid PointsMembershipChangeDTO dto);

    Result receiverPoints(ReferralDTO referralDTO);

    Result consumePoints(@Valid PointsMembershipChangeDTO dto);

    Result deletePoints(@Valid PointsMembershipChangeDTO dto);

    Result<String> giveInviteVIPGiftPoints(ReferralDTO dto);
    
}
