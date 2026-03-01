package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.LoginFormDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.User;
import com.backend.careerplanningbackend.domain.vo.LoginVO;
import com.backend.careerplanningbackend.service.UserService;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

/**
 * UserController
 * @module UserController
 */
@RestController
@RequestMapping("/user")
public class UserController {
    @Autowired
    private UserService userService;
    // apifox 的注解方法模板
    /**
     * 登录
     *
     * @param user 包含用户信息的对象，包括用户名、邮箱、密码和用户类型
     * @return 创建成功的用户信息
     */
    @PostMapping("/login")
    public Result login(@RequestBody LoginFormDTO user) {
        return userService.login(user);
    }
    /**
     * 注册
     */
    @PostMapping("/register")
    public Result register(@RequestBody LoginFormDTO user) {
        return userService.register(user);
    }
    /**
     * 忘记密码
     */
    @PutMapping("/forget")
    public Result forget(@RequestBody LoginFormDTO user) {
        return userService.forget(user);
    }
    /**
     * 发送验证码
     */
    @PostMapping("/send-code")
    public Result sendCode(@RequestBody LoginFormDTO user) {
        return userService.sendCode(user);
    }
    /**
     * 修改个人信息
     */
    @PutMapping("/edit")
    public Result edit(@RequestBody User user) {
        return userService.edit(user);
    }
    
    /**
     * 查询用户信息
     */
    @GetMapping("/info")
    public Result getUserInfo() {
        return userService.getUserInfo();
    }
    /**
     * 更换头像
     */
    @GetMapping("/avatar")
    public Result updateAvatar(MultipartFile avatar) throws IOException {
        return userService.updateAvatar(avatar);
    }
    /**
     * 更新 双token
     */
    @PostMapping("refreshToken")
    public Result refreshToken(@RequestBody LoginVO loginVO, HttpServletResponse response){
        String refreshToken=loginVO.getRefreshToken();
        return userService.refreshToken(refreshToken,response);
    }
}
