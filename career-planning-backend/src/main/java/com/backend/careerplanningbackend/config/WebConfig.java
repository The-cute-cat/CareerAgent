package com.backend.careerplanningbackend.config;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
@RequiredArgsConstructor
public class WebConfig implements WebMvcConfigurer {

    private final LoginInterceptor loginInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
         // 暂时不启用拦截器
         registry.addInterceptor(loginInterceptor)
                 .addPathPatterns("/**")//设置拦截器拦截的请求路径（ /** 表示拦截所有请求）
                 .excludePathPatterns("/user/login","/user/register",
                         "/user/send-code","/user/forget","/user/refreshToken"
                 );//设置不拦截的请求路径
    }
//    @Override
//    public void addInterceptors(InterceptorRegistry registry) {
//        registry.addInterceptor(loginInterceptor)
//                .addPathPatterns("/**")//设置拦截器拦截的请求路径（ /** 表示拦截所有请求）
//                .excludePathPatterns("/**");//暂时不拦截任何请求
//    }
}