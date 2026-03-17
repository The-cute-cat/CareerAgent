package com.backend.careerplanningbackend;

import org.junit.jupiter.api.Test;

import static com.backend.careerplanningbackend.util.AITokenUtil.checkToken;
import static com.backend.careerplanningbackend.util.AITokenUtil.createToken;

public class AiTokenTest {
    @Test
    public void testTokenGeneration() {
        // 模拟生成 AI Token 的逻辑
        String token = createToken();
        System.out.println("Generated AI Token: " + token);
        boolean b = checkToken(token);
        System.out.println("checkToken: " + b);
    }
}