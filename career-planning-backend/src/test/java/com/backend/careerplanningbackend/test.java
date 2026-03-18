package com.backend.careerplanningbackend;

import com.backend.careerplanningbackend.util.AITokenUtil;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class ATest {

    @Test
    void testAiToken() {
        String token = AITokenUtil.createToken();
        System.out.println(token);
        System.out.println(AITokenUtil.checkToken(token));
    }
}
