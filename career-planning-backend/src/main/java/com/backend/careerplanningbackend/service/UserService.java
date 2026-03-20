package com.backend.careerplanningbackend.service;

import com.backend.careerplanningbackend.domain.dto.LoginFormDTO;
import com.backend.careerplanningbackend.domain.dto.UserDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.User;
import com.backend.careerplanningbackend.domain.po.UserStuInfo;
import com.backend.careerplanningbackend.domain.vo.LoginVO;
import com.baomidou.mybatisplus.extension.service.IService;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

public interface UserService extends IService<User> {

    Result<LoginVO> login(LoginFormDTO user);

    Result<String> register(LoginFormDTO user);

    Result<String> forget(LoginFormDTO user);

    Result<String> sendCode(LoginFormDTO user);

    Result<String> sendCodeRegister(LoginFormDTO user);

    Result<String> sendCodeForget(LoginFormDTO user);

    Result<String> edit(User user);

    Result<LoginVO> refreshToken(String accessToken, HttpServletResponse response);

    Result<UserDTO> getUserInfo();

    Result<String> updateAvatar(MultipartFile avatar) throws IOException;

    Result<UserStuInfo> getUserBasicFileInfoService();
}
