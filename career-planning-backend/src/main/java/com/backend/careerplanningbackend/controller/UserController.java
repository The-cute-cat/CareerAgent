package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.LoginFormDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

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

    @PostMapping("/forget")
    public Result forget(@RequestBody LoginFormDTO user) {
        return userService.forget(user);
    }
    
    @PostMapping("/send-code")
    public Result sendCode(@RequestBody LoginFormDTO user) {
        return userService.sendCode(user);
    }
}
