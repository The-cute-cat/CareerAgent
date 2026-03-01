package com.backend.careerplanningbackend.util;

public class AITokenUtil {

    /**
     * 私有构造函数，防止实例化
     */
    private AITokenUtil() {
        throw new IllegalStateException("Utility class");
    }

    /**
     * 创建一个新的 AI 令牌。
     * <p>
     * 令牌生成流程如下：
     * 1. 将当前系统时间（毫秒）与预设的固定字符串拼接，用 "|" 分隔。
     * 2. 对拼接后的原始字符串进行 Base64 编码。
     * 3. 使用 BCrypt 算法对原始字符串进行哈希。
     * 4. 最终令牌由以下部分组合而成：BCrypt 哈希值的前7位、Base64 编码后的字符串长度、
     *    Base64 编码后的字符串本身，以及 BCrypt 哈希值的剩余部分。
     *    （Base64 字符串的长度被嵌入，以便在验证时快速定位其边界。）
     * </p>
     *
     * @return 新生成的、唯一的 AI 令牌字符串。
     */
    public static String createToken() {
        String str = System.currentTimeMillis() + "|" + "CareerAgent";
        String strBase64 = Base64Utils.encode(str);
        String encryptStr = EncryptSensitiveData.hashData(str);
        return encryptStr.substring(0, 7) + strBase64.length() + "." + strBase64 + encryptStr.substring(7);
    }

    /**
     * 检查给定的令牌是否有效。
     * <p>
     * 令牌有效性的判断标准：
     * 1. 令牌本身不为 null。
     * 2. 令牌能够被正确解析出其组成部分：哈希前缀、Base64 长度、Base64 数据和哈希后缀。
     * 3. Base64 编码的数据能够成功解码回原始字符串。
     * 4. 解码出的原始字符串中的时间戳在有效有效期内。
     * 5. 通过验证原始字符串与令牌中的哈希信息是否匹配。
     * </p>
     *
     * @param token 要验证的 AI 令牌字符串。
     * @return 如果令牌有效且未过期，则返回 `true`；否则返回 `false`。
     */
    public static boolean checkToken(String token) {
        if (token == null) {
            return false;
        }
        try {
            int index = token.indexOf(".");
            int length = Integer.parseInt(token.substring(7, index));
            String preStr = Base64Utils.decode(token.substring(index + 1, index + 1 + length));
            long time = Long.parseLong(preStr.substring(0, preStr.indexOf("|")));
            if (System.currentTimeMillis() - time > 1800 * 1000) {
                return false;
            }
            String waitCheckStr = token.substring(0, 7) + token.substring(index + 1 + length);
            return EncryptSensitiveData.checkData(preStr, waitCheckStr);
        } catch (NumberFormatException e) {
            return false;
        }
    }
}
