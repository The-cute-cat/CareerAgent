package com.backend.careerplanningbackend.config;
import cn.hutool.core.util.StrUtil;
import com.backend.careerplanningbackend.util.JwtUtil;
import com.backend.careerplanningbackend.util.ThreadLocalUtil;
import io.jsonwebtoken.Claims;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;


@Component
public class LoginInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
//        System.out.println("===== LoginInterceptor 开始处理请求 =====");
        System.out.println("请求路径: " + request.getRequestURI());
        String accessToken = request.getHeader("Authorization");

        if (StrUtil.isBlank(accessToken)) {
            //没有短token  401
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("未携带token");
            return false;
        }
        // 3. 移除Bearer前缀（如果前端添加了的话）
        if (accessToken.startsWith("Bearer ")) {
            accessToken = accessToken.substring(7);
        }

        try{
            // 4. 验证token有效性    401
            if (JwtUtil.isTokenExpired(accessToken)) { 
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.getWriter().write("token已过期");
                return false;
            }

            // 5. 解析token获取用户信息
            Claims claims = JwtUtil.parseToken(accessToken);
            String userId = claims.getSubject();
            // 将用户ID存入ThreadLocal供后续使用
            ThreadLocalUtil.set(userId);
            return true;

        } catch (Exception e) {
            //token无效
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("token无效,短token过期了");
            return false;
        }
    }
    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) throws Exception {
        ThreadLocalUtil.remove(); // 无论请求成功与否，最终都清理
    }
}
