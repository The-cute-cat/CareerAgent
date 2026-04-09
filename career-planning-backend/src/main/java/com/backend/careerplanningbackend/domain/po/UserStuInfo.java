package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * UserStuInfo
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@TableName("user_stu_info")
public class UserStuInfo {
    /**
     * 学生学历信息表
     */
    private Long id;
    /**
     * 关联sys_user ID
     */
    private Long userId;
    /**
     * 真实姓名
     */
    private String realName;
    /**
     * github_name
     */
    private String githubName;
    /**
     * gitee_name
     */
    private String giteeName;
    /**
     * 手机号码
     */
    private String phone;
    /**
     * 个人简介
     */
    private String bio;
    /**
     * 就读高校
     */
    private String school;
    /**
     * 专业
     */
    private String major;
    /**
     * 学历: 本科, 硕士, 博士
     */
    private String eduLevel;
    /**
     * 入学年份（如 2023）
     */
    private Integer startYear;
    /**
     * 毕业年份
     */
    private Integer gradYear;
    /**
     * 就业意愿描述
     */
    private String careerIntention;
    /**
     * 逻辑删除-1表示逻辑删除
     */
    private Integer isDeleted;
    /**
     * 创建时间
     */
    private LocalDateTime createTime;
    /**
     * 修改时间
     */
    private LocalDateTime updateTime;
}
