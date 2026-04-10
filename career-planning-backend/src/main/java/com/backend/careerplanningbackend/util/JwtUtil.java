package com.backend.careerplanningbackend.util;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import javax.crypto.SecretKey;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
//生成双token

@Component
public class JwtUtil {
    // 使用安全的密钥生成方式（HS256算法需要至少256位密钥）
    private static SecretKey secret;

    @Value("${jwt.secret:ThisIsSecretKeyForHelloWorldProject20250715}")
    public void setSecretString(String secretString) {
        JwtUtil.secret = Keys.hmacShaKeyFor(secretString.getBytes());
    }
    
//    private static final String secret="ThisIsSecretKeyForHopeProject2025715";

    // Token过期时间配置
    //todo
//    private static final long ACCESS_TOKEN_EXPIRE = 30 * 60 * 1000; // 30分钟
    private static final long ACCESS_TOKEN_EXPIRE = 30 * 60 * 10000000; // 本地测试
    private static final long REFRESH_TOKEN_EXPIRE = 7 * 24 * 60 * 60 * 1000; // 7天

    //携带用户的基础信息
    public static String createToken(String id) {
        Map<String, Object> claims =new HashMap<>();
        claims.put("createToken","createToken");
        claims.put("id",id);
        return  Jwts.builder()
                //头部
                .claims(claims)
                .setSubject(id)
//                .setHeaderParam("typ", "jwp")
//                .setHeaderParam("alg", "HS256")
                //载荷
                .setId(UUID.randomUUID().toString())
                .header().type("JWT").and()
                .header().keyId(UUID.randomUUID().toString()).and()
                .expiration(new Date(System.currentTimeMillis() + ACCESS_TOKEN_EXPIRE))
                .signWith(secret)
                .compact();
    }
    public static String createRefreshToken(String id) {
        Map<String, Object> claims =new HashMap<>();
        claims.put("createToken","createToken");
        claims.put("id",id);
        claims.put("reason","i don't know");
        return Jwts.builder()
                .header().type("JWT").and()
                .header().keyId(UUID.randomUUID().toString()).and()
                .expiration(new Date(System.currentTimeMillis() + REFRESH_TOKEN_EXPIRE))
                .claims(claims)
                .setSubject(id)//主题
                .signWith(secret)
                .compact();
    }

    // 解析Token
    public static Claims parseToken(String jwtToken) {
        return Jwts.parser().verifyWith(secret).build().parseSignedClaims(jwtToken).getPayload();
    }
    // 验证Token是否过期
    //判断现在的时间
    public static boolean isTokenExpired(String token) {
        Claims claims = parseToken(token);
        return claims.getExpiration().before(new Date());
    }
    //短token更新
    public static String refreshAccessToken(String refreshToken) {
        Claims claims = parseToken(refreshToken);          // 解析 refreshToken
        String name = claims.getSubject();
        return createToken(name);
    }
}