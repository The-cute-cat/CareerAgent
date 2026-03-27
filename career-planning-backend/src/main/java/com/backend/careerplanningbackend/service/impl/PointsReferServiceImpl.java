package com.backend.careerplanningbackend.service.impl;

import cn.hutool.core.bean.BeanUtil;
import com.backend.careerplanningbackend.domain.dto.PointsChangeDTO;
import com.backend.careerplanningbackend.domain.dto.ReferralDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.UserPoints;
import com.backend.careerplanningbackend.domain.vo.UserPointsVO;
import com.backend.careerplanningbackend.mapper.PointsReferMapper;
import com.backend.careerplanningbackend.service.PointsReferService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class PointsReferServiceImpl implements PointsReferService {

    private final PointsReferMapper pointsReferMapper;
    
    @Override
    public Result<UserPointsVO> getAccountPoints(Long id) {
        UserPoints accountPoints = pointsReferMapper.getAccountPoints(id);
        UserPointsVO userPointsVO = BeanUtil.copyProperties(accountPoints, UserPointsVO.class);
        return Result.ok(userPointsVO);
    }

    @Override
    public Result register(ReferralDTO referralDTO) {
        return null;
    }

    @Override
    public Result invite(ReferralDTO referralDTO) {
        return null;
    }

    @Override
    public Result registerStudent(ReferralDTO referralDTO) {
        return null;
    }

    @Override
    public Result recharge(PointsChangeDTO dto) {
        return null;
    }

    @Override
    public Result consumePoints(PointsChangeDTO dto) {
        return null;
    }

    @Override
    public Result deletePoints(PointsChangeDTO dto) {

        return null;
    }
}
