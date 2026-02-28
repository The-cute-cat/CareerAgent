package com.backend.careerplanningbackend.util;

public class RedisConstant {
    /** 验证码 key 前缀 */
    public static final String EMAIL_CODE = "email:code:";
    /** 验证码 key 计数 这个用来计算60秒内是否重置 */
    public static final String EMAIL_SENT = "email:sent:";
    /** 有效期 300 秒 */
    public static final long EXPIRE_TIME = 300L;
    /** 防刷时隔 60 秒 */
    public static final long SENT_TIME = 60L;
    /* 商家的key */
    public static final String CACHE_MERCHANT_KEY = "cache:merchant:";
    /** 有效期 30 分钟 */
    public static final long CACHE_MERCHANT_TTL = 30L;
    /* 缓存穿透 空值时间 */
    public static final long CACHE_NULL_TTL = 2L;
    /* 商家的key */
    public static final String LOCAL_MERCHANT_KEY = "lock:merchant:";
    /* 这是 ai智能助手缓存前缀*/
    public static final String AI_KEY_PREFIX = "chat:memory:";

    /* 缓存 ai智能助手*/
    public static final long AI_ASSISTANT_TTL = 7L;


}
