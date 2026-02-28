package com.backend.careerplanningbackend.mapper;

import com.backend.careerplanningbackend.domain.dto.LoginFormDTO;
import com.backend.careerplanningbackend.domain.dto.UserDTO;
import com.backend.careerplanningbackend.domain.po.User;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
    User selectByUsername(String username);

    User selectByEmail(String email);

    int register(LoginFormDTO user);

    int forget(LoginFormDTO user);

    int edit(User user);

    User getUserAllInfo(Long id);

    UserDTO getUserInfo(Long id);

    int updateAvatar(String upload, Long id);
}
