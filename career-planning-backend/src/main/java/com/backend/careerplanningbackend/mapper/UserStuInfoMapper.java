package com.backend.careerplanningbackend.mapper;

import com.backend.careerplanningbackend.domain.po.UserStuInfo;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface UserStuInfoMapper extends BaseMapper<UserStuInfo> {

    @Select("select * from user_stu_info where user_id = #{currentUserId}")
    UserStuInfo getUserBasicFileInfoService(Long currentUserId);


}
