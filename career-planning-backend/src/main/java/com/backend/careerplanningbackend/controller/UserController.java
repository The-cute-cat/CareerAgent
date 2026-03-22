package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.LoginFormDTO;
import com.backend.careerplanningbackend.domain.dto.UserDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.User;
import com.backend.careerplanningbackend.domain.po.UserStuInfo;
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
     * login
     * 登录
     *
     * @param user 包含用户信息的对象，包括用户名、邮箱、密码和用户类型
     * @return 创建成功的用户信息
     */
    @PostMapping("/login")
    public Result<LoginVO> login(@RequestBody LoginFormDTO user) {
        log.info("login接收到的登录参数: {}", user.toString()); // 需要在 DTO 中重写 toString()
        return userService.login(user);
    }
    /**
     * register
     * 注册
     */
    @PostMapping("/register")
    public Result<String> register(@RequestBody LoginFormDTO user) {
        log.info("register接收到的注册参数: {}", user.toString()); 
        return userService.register(user);
    }
    /**
     * forget
     * 忘记密码
     */
    @PutMapping("/forget-password")
    public Result<String> forget(@RequestBody LoginFormDTO user) {
        log.info("forget-password接收到的参数: {}", user.toString());
        return userService.forget(user);
    }
    /**
     * sendCodeRegister
     * 发送注册验证码
     */
    @PostMapping("/send-code-register")
    public Result<String> sendCodeRegister(@RequestBody LoginFormDTO user) {
        log.info("send-code-register接收到的参数: {}", user.toString());
        return userService.sendCodeRegister(user);
    }
    /**
     * sendCodeForget
     * 发送注册验证码
     */
    @PostMapping("/send-code-forget")
    public Result<String> sendCodeForget(@RequestBody LoginFormDTO user) {
        log.info("send-code-forget接收到的参数: {}", user.toString());
        return userService.sendCodeForget(user);
    }
    /**
     * edit
     * 修改个人信息
     */
    @PutMapping("/edit")
    public Result<String> edit(@RequestBody User user) {
        log.info("edit接收到的参数: {}", user.toString());
        return userService.edit(user);
    }
    
    /**
     * getUserInfo
     * 查询用户信息
     */
    @GetMapping("/get-user-info")
    public Result<UserDTO> getUserInfo() {
        log.info("get-user-info请求");
        return userService.getUserInfo();
    }

    /**
     * getUserBasicFileInfoService
     * 查询用户基础档案信息
     */
    @GetMapping("/get-basic-info")
    public Result<UserStuInfo> getUserBasicFileInfoService() {
        log.info("/user/get-basic-fileInfo请求");
        return userService.getUserBasicFileInfoService();
    }

    /**
     * updateAvatar
     * 更换头像
     */
    @GetMapping("/avatar")
    public Result<String> updateAvatar(MultipartFile avatar) throws IOException {
        log.info("updateAvatar接收到的参数: {}", avatar.getOriginalFilename());
        return userService.updateAvatar(avatar);
    }
    /**
     * refreshToken
     * 更新 双token
     */
    @PostMapping("refreshToken")
    public Result<LoginVO> refreshToken(@RequestBody LoginVO loginVO, HttpServletResponse response){
        log.info("refreshToken接收到的参数: {}", loginVO.toString());
        String refreshToken=loginVO.getRefreshToken();
        return userService.refreshToken(refreshToken,response);
    }
}
