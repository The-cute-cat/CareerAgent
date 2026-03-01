package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.LoginFormDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.User;
import com.backend.careerplanningbackend.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("/user")
public class UserController {
    @Autowired
    private UserService userService;
    
    @PostMapping("/login")
    public Result login(@RequestBody LoginFormDTO user) {
        return userService.login(user);
    }

    @PostMapping("/register")
    public Result register(@RequestBody LoginFormDTO user) {
        return userService.register(user);
    }

    @PutMapping("/forget")
    public Result forget(@RequestBody LoginFormDTO user) {
        return userService.forget(user);
    }
    
    @PostMapping("/send-code")
    public Result sendCode(@RequestBody LoginFormDTO user) {
        return userService.sendCode(user);
    }

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
    
    @GetMapping("/avatar")
    public Result updateAvatar(MultipartFile avatar) throws IOException {
        return userService.updateAvatar(avatar);
    }
}
