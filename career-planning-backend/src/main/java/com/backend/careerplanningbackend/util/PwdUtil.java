package com.backend.careerplanningbackend.util;

import cn.hutool.crypto.digest.BCrypt;
public class PwdUtil {
    /**
     * 私有构造函数，防止实例化
     */
    private PwdUtil(){
        throw new IllegalStateException("Utility class");
    }
    private static final int BCRYPT_ROUNDS = 12;
    
    // 加密
    public static String encode(String rawPassword) {
        return BCrypt.hashpw(rawPassword, BCrypt.gensalt(BCRYPT_ROUNDS));
    }

    // 验证
    public static boolean match(String rawPassword, String encodedPassword) {
        return BCrypt.checkpw(rawPassword, encodedPassword);
    }
}