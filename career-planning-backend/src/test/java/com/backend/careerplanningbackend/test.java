package com.backend.careerplanningbackend;

import cn.hutool.crypto.digest.BCrypt;

public class test {
    public static void main(String[] args) {
        String hashed = BCrypt.hashpw("123456", BCrypt.gensalt());
        System.out.println(hashed);
        // 输出的字符串通常是以 $2a$10$ 开头的

    }
}
