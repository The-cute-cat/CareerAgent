package com.backend.careerplanningbackend.service.impl;

import com.backend.careerplanningbackend.domain.po.InterviewQuestion;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.mapper.InterviewQuestionMapper;
import com.backend.careerplanningbackend.service.InterviewQAService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.stereotype.Service;
import java.util.*;

/**
 * 八股文问答业务实现
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class InterviewQuestionServiceImpl
        extends ServiceImpl<InterviewQuestionMapper, InterviewQuestion>
        implements InterviewQAService {

    private final InterviewQuestionMapper interviewQuestionMapper;

    private final ChatClient chatClient;

    @Override
    public Result<List<InterviewQAItem>> generateQA(InterviewQAGenerateRequest request) {
        log.info("生成八股文问答: {}", request);
//        interviewQuestionMapper.insert(request)
        chatClient.prompt()
                .user("这是用户传输的请求体"+request+"请你根据它的内容生成八股文问答")
                .call()
                .content();
        return null;
    }

    @Override
    public Result<List<InterviewQAItem>> generateAndStoreQA(InterviewQAGenerateRequest request) {
        log.info("生成八股文问答并存储: {}", request);
//        interviewQuestionMapper.insert(request)
        chatClient.prompt()
                .user("这是用户传输的请求体"+request+"请你根据它的内容生成八股文问答")
                .call()
                .content();
        return null;
    }

    @Override
    public Result<List<InterviewQAItem>> queryQA(String topic, String stackLevel) {
        log.info("查询八股文问答: topic={}, stackLevel={}", topic, stackLevel);
        return null;
    }
}