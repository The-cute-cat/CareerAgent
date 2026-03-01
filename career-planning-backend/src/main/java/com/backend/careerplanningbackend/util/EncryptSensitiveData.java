package com.backend.careerplanningbackend.util;

import org.mindrot.jbcrypt.BCrypt;

public class EncryptSensitiveData {//bcrypt算法
    /**
     * 私有构造函数，防止实例化
     */
    private EncryptSensitiveData(){
        throw new IllegalStateException("Utility class");
    }

    private static final int BCRYPT_ROUNDS = 12;
    /**
     * 使用 bcrypt 对敏感数据进行哈希处理。
     * @param Data 需要哈希的原始数据字符串。
     * @return 哈希后的字符串，包含 salt 和哈希结果。
     */
    public static String hashData(String Data) {
        return BCrypt.hashpw(Data, BCrypt.gensalt(BCRYPT_ROUNDS));
    }

    /**
     * 验证原始数据是否与哈希值匹配。
     * @param Data 待验证的原始数据字符串。
     * @param hashedData 之前生成的哈希字符串。
     * @return 如果原始数据与哈希值匹配返回 true，否则返回 false。
     */
    public static boolean checkData(String Data, String hashedData) {
        return BCrypt.checkpw(Data, hashedData);
    }
}