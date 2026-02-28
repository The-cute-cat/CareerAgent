package com.backend.careerplanningbackend.util;

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
}
