package com.backend.careerplanningbackend.config;

import com.alipay.api.AlipayClient;
import com.alipay.api.DefaultAlipayClient;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Data
@Configuration
@ConfigurationProperties(prefix = "alipay")   // ① 一次性映射整个前缀
public class AliPayConfig {
    /**
     * 支付宝支付配置
     */
    // ② 成员变量名必须和 yml 里的 key 一模一样（驼峰）
    private String gateway;
    private String appId;
    private String privateKey;
    private String publicKey;
    private String notifyUrl;
    private String returnUrl;

    // ③ 把 AlipayClient 交给 Spring 容器，以后 @Autowired 就能用
    @Bean
    public AlipayClient alipayClient() {
        return new DefaultAlipayClient(
                gateway,
                appId,
                privateKey,
                "json",      // 固定
                "UTF-8",     // 固定
                publicKey,
                "RSA2");     // 固定
    }
}