package com.backend.careerplanningbackend.domain.po;

import lombok.Data;

/**
 * UserStuInfo
 */
@Data
public class UserStuInfo {
    /**
     * 学生学历信息表
     */
    private long id;
    /**
     * 关联sys_user ID
     */
    private long userid;
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
    private Long startYear;
    /**
     * 毕业年份
     */
    private Long gradYear;
    /**
     * 就业意愿描述
     */
    private String careerIntention;
    /**
     * 逻辑删除-1表示逻辑删除
     */
    private Long isDeleted;
    /**
     * 创建时间
     */
    private String createTime;
    /**
     * 修改时间
     */
    private String updateTime;
}
