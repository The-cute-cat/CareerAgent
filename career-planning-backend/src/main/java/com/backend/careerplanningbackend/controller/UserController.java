package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.LoginFormDTO;
import com.backend.careerplanningbackend.domain.dto.UserDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.User;
import com.backend.careerplanningbackend.domain.vo.LoginVO;
import com.backend.careerplanningbackend.service.UserService;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

/**
 * UserController
 */
@Slf4j
@RestController
@RequestMapping("/user")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;
    /**
     * 登录
     *
     * @param user 包含用户信息的对象，包括用户名、邮箱、密码和用户类型
     * @return 创建成功的用户信息
     */
    @PostMapping("/login")
    public Result<LoginVO> login(@RequestBody LoginFormDTO user) {
        log.info("接收到的登录参数: {}", user.toString()); // 需要在 DTO 中重写 toString()
        return userService.login(user);
    }
    /**
     * 注册
     */
    @PostMapping("/register")
    public Result<String> register(@RequestBody LoginFormDTO user) {
        return userService.register(user);
    }
    /**
     * 忘记密码
     */
    @PutMapping("/forget-password")
    public Result<String> forget(@RequestBody LoginFormDTO user) {
        return userService.forget(user);
    }
    /**
     * 发送注册验证码
     */
    @PostMapping("/send-code-register")
    public Result<String> sendCodeRegister(@RequestBody LoginFormDTO user) {
        return userService.sendCodeRegister(user);
    }
    /**
     * 发送注册验证码
     */
    @PostMapping("/send-code-forget")
    public Result<String> sendCodeForget(@RequestBody LoginFormDTO user) {
        return userService.sendCodeForget(user);
    }
    /**
     * 修改个人信息
     */
    @PutMapping("/edit")
    public Result<String> edit(@RequestBody User user) {
        return userService.edit(user);
    }
    
    /**
     * 查询用户信息
     */
    @GetMapping("/get-user-info")
    public Result<UserDTO> getUserInfo() {
        return userService.getUserInfo();
    }
    /**
     * 更换头像
     */
    @GetMapping("/avatar")
    public Result<String> updateAvatar(MultipartFile avatar) throws IOException {
        return userService.updateAvatar(avatar);
    }
    /**
     * 更新 双token
     */
    @PostMapping("refreshToken")
    public Result<LoginVO> refreshToken(@RequestBody LoginVO loginVO, HttpServletResponse response){
        String refreshToken=loginVO.getRefreshToken();
        return userService.refreshToken(refreshToken,response);
    }
}
