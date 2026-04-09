package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.beans.factory.annotation.Value;

@Data
@NoArgsConstructor
@AllArgsConstructor
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
    // 邀请码
    private String inviteCode;
    
    @Override
    public String toString() {
        return "LoginFormDTO{username='" + username + "', email='" + email + "'}";
    }

}
