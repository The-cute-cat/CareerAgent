package com.backend.careerplanningbackend.domain.po;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class UserAuth {
    private Long id;

    /** 关联 sys_user.id */
    private Long userId;

    /** 登录类型：1-学号/工号，2-手机号，3-邮箱，4-微信 */
    private Integer identityType;

    /** 标识符：存具体的学号、手机号、邮箱或微信OpenID */
    private String identifier;

    /** 凭证：密码的哈希值（如果是验证码/微信登录，此字段可为空） */
    private String password;

    /** 绑定时间 */
    private LocalDateTime createdAt;

    /** 更新时间 */
    private LocalDateTime updatedAt;
}
