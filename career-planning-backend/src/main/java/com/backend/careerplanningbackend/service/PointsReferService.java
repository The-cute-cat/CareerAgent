package com.backend.careerplanningbackend.service;

import com.backend.careerplanningbackend.domain.dto.PaymentCreateDTO;
import com.backend.careerplanningbackend.domain.dto.PointsMembershipChangeDTO;
import com.backend.careerplanningbackend.domain.dto.ReferralDTO;
import com.backend.careerplanningbackend.domain.dto.StudentTrueDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.UserPoints;
import com.backend.careerplanningbackend.domain.vo.UserPointsVO;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;

public interface PointsReferService {


    Result<UserPointsVO> getAccountPoints(Long userId);

    Result<Object> register(ReferralDTO referralDTO);

    Result<ReferralDTO> generateInvite(ReferralDTO referralDTO);
    
    Result<Object> registerStudent(StudentTrueDTO studentTrueDTO);

    Result<Long> recharge(@Valid PaymentCreateDTO paymentCreateDTO);

    Result receiverPoints(ReferralDTO referralDTO);

    Result<UserPoints> consumePoints(@Valid PointsMembershipChangeDTO dto);

    Result<String> giveInviteVIPGiftPoints(ReferralDTO dto);

    Result<Object> deletePoints(@Valid PointsMembershipChangeDTO dto);
    
}
