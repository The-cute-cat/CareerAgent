package com.backend.careerplanningbackend.domain.dto;

import lombok.Data;

@Data
public class LoginFormDTO {
    // 用户名
    private String username;
    // 密码
    private String password;
    // 确认密码(二次密码)
    private String passwordConfirm;
    // 邮箱
    private String email;
    // 验证码
    private String code;
}
