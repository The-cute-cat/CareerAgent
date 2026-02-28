package com.backend.careerplanningbackend.util;

import cn.hutool.crypto.digest.BCrypt;
public class PwdUtil {
    // 加密
    public static String encode(String rawPassword) {
        return BCrypt.hashpw(rawPassword, BCrypt.gensalt(12));
    }

    // 验证
    public static boolean match(String rawPassword, String encodedPassword) {
        return BCrypt.checkpw(rawPassword, encodedPassword);
    }
}