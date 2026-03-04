package com.backend.careerplanningbackend.util;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;

import javax.crypto.SecretKey;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
//生成双token

public class JwtUtil {
    // 使用安全的密钥生成方式（HS256算法需要至少256位密钥）
    private static final String secretString="ThisIsSecretKeyForHopeProject2025715";
    private static final SecretKey secret = Keys.hmacShaKeyFor(secretString.getBytes());

    // Token过期时间配置
    private static final long ACCESS_TOKEN_EXPIRE = 30 * 60 * 100000; // 30分钟
    private static final long REFRESH_TOKEN_EXPIRE = 7 * 24 * 60 * 60 * 1000; // 7天

    //携带用户的基础信息
    public static String createToken(String id) {
        Map<String, Object> claims =new HashMap<>();
        claims.put("createToken","createToken");
        claims.put("id",id);
        JwtBuilder jwtBuilder = Jwts.builder();

        return jwtBuilder
                //头部
                .setClaims(claims)
                .setHeaderParam("typ", "jwp")
                .setHeaderParam("alg", "HS256")
                //载荷
                .setId(UUID.randomUUID().toString())
                .setSubject(id)
                .setIssuedAt(new Date())//签发时间
                .setExpiration(new Date(System.currentTimeMillis() + ACCESS_TOKEN_EXPIRE))//截止时间
                //签名
                .signWith(secret)
                .compact();
    }
    //只携带基础信息
    public static String createRefreshToken(String id) {
        Map<String, Object> claims =new HashMap<>();
        claims.put("createToken","createToken");
        claims.put("id",id);
        claims.put("reason","i don't know");
        JwtBuilder jwtBuilder = Jwts.builder();
        return jwtBuilder
                //头部
                .setClaims(claims)
                .setHeaderParam("typ", "jwp")
                .setHeaderParam("alg", "HS256")
                //载荷
                .setId(UUID.randomUUID().toString())
                .setSubject(id)//主题
                .setIssuedAt(new Date())//签发时间
                .setExpiration(new Date(System.currentTimeMillis() + REFRESH_TOKEN_EXPIRE))//截止时间
                //签名
                .signWith(secret)
                .compact();
    }

    // 解析Token
    public static Claims parseToken(String jwtToken) {
        return Jwts.parserBuilder()
                .setSigningKey(secret)
                .build()
                .parseClaimsJws(jwtToken)
                .getBody();
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