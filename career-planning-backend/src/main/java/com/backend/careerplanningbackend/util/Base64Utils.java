package com.backend.careerplanningbackend.util;

import java.nio.charset.StandardCharsets;
import java.util.Base64;

/**
 * Base64编码/解码工具类
 *
 * <p>提供将字符串进行Base64编码以及将Base64字符串解码回原字符串的功能。</p>
 */
public class Base64Utils {

    private static final Base64.Encoder encoder = Base64.getEncoder();
    private static final Base64.Decoder decoder = Base64.getDecoder();

    /**
     * 私有构造函数，防止实例化
     */
    private Base64Utils() {
        throw new IllegalStateException("Utility class");
    }

    /**
     * 将原始字符串编码为Base64字符串。
     *
     * @param plainText 待编码的原始字符串。
     * @return 编码后的Base64字符串。如果输入为null，则返回null。
     */
    public static String encode(String plainText) {
        if (plainText == null) {
            return null;
        }
        byte[] textBytes = plainText.getBytes(StandardCharsets.UTF_8);
        return encoder.encodeToString(textBytes);
    }

    /**
     * 将Base64字符串解码为原始字符串。
     *
     * @param base64Text 待解码的Base64字符串。
     * @return 解码后的原始字符串。如果输入为null，则返回null。
     * @throws IllegalArgumentException 如果输入的base64Text不是有效的Base64字符串。
     */
    public static String decode(String base64Text) {
        if (base64Text == null) {
            return null;
        }
        try {
            byte[] textBytes = decoder.decode(base64Text);
            return new String(textBytes, StandardCharsets.UTF_8);
        } catch (IllegalArgumentException e) {
            System.err.println("Invalid Base64 string input: " + base64Text);
            throw e;
        }
    }

}
