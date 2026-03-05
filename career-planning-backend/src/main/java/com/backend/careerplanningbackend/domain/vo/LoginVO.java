package com.backend.careerplanningbackend.domain.vo;

import com.backend.careerplanningbackend.domain.dto.UserDTO;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class LoginVO {
    // Token 信息
    private String accessToken;     // 访问令牌
    private String refreshToken;    // 刷新令牌
    
    // 用户信息
    private UserDTO userInfo;
//    private String id;              // 用户ID
//    private String username;        // 用户名
//    private String nickname;        // 昵称
//    private String avatar;          // 头像

    public LoginVO(String accessToken, String refreshToken) {
        this.accessToken=accessToken;
        this.refreshToken=refreshToken;
    }
//    private String role;            // 角色
//    private String email;           // 邮箱
//    private Integer status;         // 账户状态（1:启用, 0:禁用）
}
