package com.backend.careerplanningbackend.service;

import com.backend.careerplanningbackend.domain.po.Feedback;
import com.backend.careerplanningbackend.domain.po.Result;
import com.baomidou.mybatisplus.core.metadata.IPage;

import java.util.List;

/**
 * IFeedbackService
 * 用户反馈服务接口
 */
public interface IFeedbackService {
    
    /**
     * 提交用户反馈
     */
    Result<Boolean> submitFeedback(Feedback feedback);
    
    /**
     * 分页查询所有反馈
     */
    Result<IPage<Feedback>> getFeedbackList(Integer pageNum, Integer pageSize, String type);
    
    /**
     * 查询用户的反馈历史
     */
    Result<IPage<Feedback>> getUserFeedbackHistory(Long userId, Integer pageNum, Integer pageSize);
    
    /**
     * 获取反馈详情
     */
    Result<Feedback> getFeedbackById(Integer id);
    
    /**
     * 管理员回复反馈
     */
    Result<Boolean> replyFeedback(Integer id, String response);
    
    /**
     * 删除反馈
     */
    Result<Boolean> deleteFeedback(Integer id);
    
    /**
     * 查询指定类型的反馈列表
     */
    Result<List<Feedback>> getFeedbackByType(String type);
    /**
     * 更新反馈
     * @param feedback 反馈信息
     * @return 操作结果
     */
    Result<Boolean> updateFeedback(Feedback feedback);
}