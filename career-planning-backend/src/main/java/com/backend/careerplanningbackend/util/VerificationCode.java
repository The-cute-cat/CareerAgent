package com.backend.careerplanningbackend.util;

import java.util.Random;

/**
 * 生成验证码的类
 */
public class VerificationCode {
    public static String generateVerificationCode() {
        char[] chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz".toCharArray();
        Random random = new Random();
        StringBuilder code = new StringBuilder();
        for (int i = 0; i < 5; i++) {
            code.append(chars[random.nextInt(chars.length)]);
        }
        code.append(random.nextInt(10));
        return code.toString();
    }
}
