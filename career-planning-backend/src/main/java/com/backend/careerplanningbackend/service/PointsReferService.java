package com.backend.careerplanningbackend.service;

import com.backend.careerplanningbackend.domain.dto.PointsChangeDTO;
import com.backend.careerplanningbackend.domain.dto.ReferralDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import jakarta.validation.Valid;

public interface PointsReferService {


    Result getAccountPoints(Long userId);

    Result register(ReferralDTO referralDTO);

    Result invite(ReferralDTO referralDTO);

    Result registerStudent(ReferralDTO referralDTO);

    Result recharge(@Valid PointsChangeDTO dto);

    Result consumePoints(@Valid PointsChangeDTO dto);

    Result deletePoints(@Valid PointsChangeDTO dto);
}
