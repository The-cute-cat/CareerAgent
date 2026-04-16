package com.backend.careerplanningbackend.config;
import cn.hutool.core.util.StrUtil;
import com.backend.careerplanningbackend.util.JwtUtil;
import com.backend.careerplanningbackend.util.ThreadLocalUtil;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.JwtException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import java.util.Date;

@Slf4j
@Component
public class LoginInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        log.debug("===== LoginInterceptor 开始处理请求 =====");
        log.info("请求路径: {}", request.getRequestURI());
        String accessToken = request.getHeader("Authorization");

        if (StrUtil.isBlank(accessToken)) {
            log.error("未携带token");
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("未携带token");
            return false;
        }
        
        if (accessToken.startsWith("Bearer ")) {
            accessToken = accessToken.substring(7);
        }

        try {
            // 只解析一次 token，获取 Claims
            Claims claims = JwtUtil.parseToken(accessToken);
            
            // 检查token是否过期（不重复调用 parseToken）
            if (claims.getExpiration().before(new Date())) {
                log.error("token已过期");
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.getWriter().write("token已过期");
                return false;
            }

            // 获取用户ID并存入ThreadLocal供后续使用
            String userId = (String) claims.get("id");
            log.info("用户认证成功，用户ID: {}", userId);
            ThreadLocalUtil.set(userId);
            return true;

        } catch (ExpiredJwtException e) {
            log.error("LoginInterceptor.preHandle Token已过期", e);
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("短token已过期");
            return false;
        } catch (JwtException e) {
            log.error("LoginInterceptor.preHandle Token无效", e);
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("token无效");
            return false;
        }
    }
    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) throws Exception {
        log.debug("afterCompletion");
        ThreadLocalUtil.remove(); // 无论请求成功与否，最终都清理
    }
}
