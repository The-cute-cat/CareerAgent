package com.backend.careerplanningbackend.util;

import cn.hutool.core.util.StrUtil;

public class RegexUtil {
    /**
     * 是否是无效邮箱格式
     * @param email 要校验的邮箱
     * @return true:不符合规范，false：符合规范
     */
    public static boolean isEmailInvalid(String email){
        return mismatch(email, RegexPatterns.EMAIL_REGEX);
    }

    /**
     * 是否是无效验证码格式
     * @param code 要校验的验证码
     * @return true:不符合规范，false：符合规范
     */
    public static boolean isCodeInvalid(String code){
        return mismatch(code, RegexPatterns.VERIFY_CODE_REGEX);
    }
    
    /**
     * 是否是无效密码格式
     * @param email 要校验的验证码
     * @return true:不符合规范，false：符合规范
     */
    public static boolean isPasswordInvalid(String email){
        return mismatch(email, RegexPatterns.PASSWORD_REGEX);
    }
    
    /**
     * 校验用户名长度是否无效
     * @param username 用户名
     * @return true: 无效(超长或为空), false: 有效
     */
    public static boolean isUsernameInvalid(String username){
        if (StrUtil.isBlank(username)) {
            return true;
        }
        return username.length() > RegexPatterns.USERNAME_MAX_LENGTH;
    }

    // 校验是否不符合正则格式
    //--false--符合正则表达式
    private static boolean mismatch(String str, String regex){
        if (str == null || str.trim().isEmpty()) {
            return true;
        }
        return !str.matches(regex);
    }
}