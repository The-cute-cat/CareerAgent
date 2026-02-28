package com.backend.careerplanningbackend.service;

import com.backend.careerplanningbackend.domain.dto.LoginFormDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.User;
import com.baomidou.mybatisplus.extension.service.IService;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

public interface UserService extends IService<User> {

    Result login(LoginFormDTO user);

    Result register(LoginFormDTO user);

    Result forget(LoginFormDTO user);

    Result sendCode(LoginFormDTO user);


    Result edit(User user);

    Result refreshToken(String accessToken, HttpServletResponse response);

    Result getUserInfo();

    String updateAvatar(MultipartFile avatar, Long id) throws IOException;

//    void modify(ModifyFormDTO user);    
}
