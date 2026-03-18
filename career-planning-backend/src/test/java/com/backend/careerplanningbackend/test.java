package com.backend.careerplanningbackend;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.util.AITokenUtil;
import com.backend.careerplanningbackend.util.AiServiceClient;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

@SpringBootTest
class ATest {

    @Autowired
    private AiServiceClient client;

    @Test
    void testChatWithMessage() {
        List<File> files = new ArrayList<>();
        files.add(new File("C:\\Users\\The_cute_cat\\Desktop\\CareerAgent\\第十七届中国大学生服务外包创新创业大赛A13赛题.pdf"));
        AiChatResponse result = client.chatWithFiles("/parse/pdf", files, "12345");
        System.out.println(result);
    }

    @Test
    void testAiToken() {
        String token = AITokenUtil.createToken();
        System.out.println(token);
        System.out.println(AITokenUtil.checkToken(token));
    }
}
