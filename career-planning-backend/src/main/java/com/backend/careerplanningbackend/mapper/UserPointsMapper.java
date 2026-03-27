package com.backend.careerplanningbackend.mapper;

import com.backend.careerplanningbackend.domain.dto.ReferralDTO;
import com.backend.careerplanningbackend.domain.po.UserPoints;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserPointsMapper extends BaseMapper<UserPoints> {

//    @Select("select * from user_points where user_id = #{id}")
//    UserPoints getAccountPoints(Long id);

    void insertUserPoints(ReferralDTO referralDTO);
}
