package com.backend.careerplanningbackend.util;

import cn.hutool.core.util.StrUtil;

public class ThreadLocalUtil {
    //提供ThreadLocal对象  key - value 类型
    private static final ThreadLocal userThreadLocal = new ThreadLocal();

    //根据 键 存储
    public static void set(Object object) {
        userThreadLocal.set(object);
    }

    //根据 值 获取
    public static <T>T get() {
        return (T)userThreadLocal.get();
    }

    public static Object get2() {
        return userThreadLocal.get();
    }

    //清除 ThreadLocal 放置内存泄漏
    public static void remove() {
        userThreadLocal.remove();
    }

    public static Long getCurrentUserId() {
        String idStr = ThreadLocalUtil.get();
        if (StrUtil.isBlank(idStr)) {
            throw new RuntimeException("用户未登录");
        }
        return Long.parseLong(idStr);
    } 
}
