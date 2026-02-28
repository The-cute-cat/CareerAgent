package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    
    private Long id;
    /** 用户昵称 (默认显示用) */
    private String username;

    /** 用户昵称 (默认显示用) */
    private String nickname;

    /** 邮箱 */
    private String email;
    
    private String password;
    
    private String passwordConfirm;

    /** 用户头像URL */
    private String avatar;

    /** 角色：1-学生，2-指导老师，3-系统管理员 */
    private Integer role;

    /** 账号状态：0-禁用，1-启用 */
    private Integer status;

    /** 注册时间 */
    private LocalDateTime createdAt;

    /** 更新时间 */
    private LocalDateTime updatedAt;
}
