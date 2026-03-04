package com.backend.careerplanningbackend.domain.vo;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class LoginVO {
    // Token 信息
    private String accessToken;     // 访问令牌
    private String refreshToken;    // 刷新令牌
    
//    // 用户信息
//    private String id;              // 用户ID
//    private String username;        // 用户名
//    private String nickname;        // 昵称
//    private String avatar;          // 头像
//    private String role;            // 角色
//    private String email;           // 邮箱
//    private Integer status;         // 账户状态（1:启用, 0:禁用）
}
