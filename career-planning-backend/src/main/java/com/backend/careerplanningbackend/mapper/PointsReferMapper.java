package com.backend.careerplanningbackend.mapper;

import com.backend.careerplanningbackend.domain.po.UserPoints;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface PointsReferMapper {

    @Select("select * from user_points where user_id = #{id}")
    UserPoints getAccountPoints(Long id);
    
    
}
