package com.backend.careerplanningbackend.service;

import com.backend.careerplanningbackend.domain.po.InterviewQuestion;
import com.backend.careerplanningbackend.domain.po.Result;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;

/**
 * 八股文问答 业务接口
 */
public interface InterviewQAService extends IService<InterviewQuestion> {
    /**
     * 根据主题和级别生成八股文 Q&A
     * @param request 请求参数
     * @return 问答列表
     */
    Result<List<InterviewQAItem>> generateQA(InterviewQAGenerateRequest request);

    /**
     * 使用 Spring AI 生成题库（同步）并存储到数据库
     * @param request 请求参数
     * @return 生成的题库列表
     */
    Result<List<InterviewQAItem>> generateAndStoreQA(InterviewQAGenerateRequest request);

    /**
     * 从数据库查询已生成的题库
     * @param topic 主题
     * @param stackLevel 技术级别
     * @return 题库列表
     */
    Result<List<InterviewQAItem>> queryQA(String topic, String stackLevel);
}

