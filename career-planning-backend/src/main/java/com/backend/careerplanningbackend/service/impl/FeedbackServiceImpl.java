package com.backend.careerplanningbackend.service.impl;

import com.backend.careerplanningbackend.domain.po.Feedback;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.mapper.FeedbackMapper;
import com.backend.careerplanningbackend.service.IFeedbackService;
import com.backend.careerplanningbackend.util.ThreadLocalUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

/**
 * FeedbackServiceImpl
 * 用户反馈业务逻辑实现类
 * 主要功能：
 * 1. 新增用户反馈
 * 2. 查询反馈列表（支持分页）
 * 3. 查询单个反馈详情
 * 4. 更新反馈或管理员回复
 * 5. 删除反馈
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class FeedbackServiceImpl extends ServiceImpl<FeedbackMapper, Feedback> implements IFeedbackService {

    private final FeedbackMapper feedbackMapper;

    /**
     * 提交用户反馈
     */
    @Transactional(rollbackFor = Exception.class)
    public Result<Boolean> submitFeedback(Feedback feedback) {
        Long currentUserId = ThreadLocalUtil.getCurrentUserId();
        feedback.setUserId(currentUserId);
        
        int rows = feedbackMapper.insert(feedback);
        if (rows > 0) {
            log.info("用户 {} 提交反馈成功，反馈类型: {}", currentUserId, feedback.getType());
            return Result.ok(true);
        } else {
            return Result.fail("反馈提交失败");
        }
    }

    /**
     * 分页查询所有反馈（支持多条件筛选）
     */
    public Result<IPage<Feedback>> getFeedbackList(Integer pageNum, Integer pageSize, String type) {
        Page<Feedback> page = new Page<>(pageNum, pageSize);
        
        LambdaQueryWrapper<Feedback> queryWrapper = new LambdaQueryWrapper<>();
        if (type != null && !type.isEmpty()) {
            queryWrapper.eq(Feedback::getType, type);
        }
        
        IPage<Feedback> result = feedbackMapper.selectPage(page, queryWrapper);
        log.info("分页查询反馈成功，页码: {}, 每页数量: {}, 总数: {}", pageNum, pageSize, result.getTotal());
        return Result.ok(result);
    }

    /**
     * 查询用户的反馈历史
     */
    public Result<IPage<Feedback>> getUserFeedbackHistory(Long userId, Integer pageNum, Integer pageSize) {
        Page<Feedback> page = new Page<>(pageNum, pageSize);
        
        LambdaQueryWrapper<Feedback> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(Feedback::getUserId, userId)
                .orderByDesc(Feedback::getId);
        
        IPage<Feedback> result = feedbackMapper.selectPage(page, queryWrapper);
        log.info("查询用户 {} 的反馈历史成功，总数: {}", userId, result.getTotal());
        return Result.ok(result);
    }

    /**
     * 获取反馈详情
     */
    public Result<Feedback> getFeedbackById(Integer id) {
        Feedback feedback = feedbackMapper.selectById(id);
        if (feedback != null) {
            log.info("查询反馈详情成功，反馈ID: {}", id);
            return Result.ok(feedback);
        } else {
            log.warn("反馈不存在，反馈ID: {}", id);
            return Result.fail("反馈不存在");
        }
    }

    /**
     * 管理员回复反馈
     */
    public Result<Boolean> replyFeedback(Integer id, String response) {
        Feedback feedback = new Feedback();
        feedback.setId(id);
        feedback.setResponse(response);
        feedback.setUpdateTime(LocalDateTime.now());
        
        int rows = feedbackMapper.updateById(feedback);
        if (rows > 0) {
            log.info("管理员回复反馈成功，反馈ID: {}", id);
            return Result.ok(true);
        } else {
            log.warn("反馈不存在或回复失败，反馈ID: {}", id);
            return Result.fail("反馈不存在或回复失败");
        }
    }

    /**
     * 删除反馈
     */
    public Result<Boolean> deleteFeedback(Integer id) {
        int rows = feedbackMapper.deleteById(id);
        if (rows > 0) {
            log.info("删除反馈成功，反馈ID: {}", id);
            return Result.ok(true);
        } else {
            log.warn("反馈不存在或删除失败，反馈ID: {}", id);
            return Result.fail("反馈不存在或删除失败");
        }
    }

    /**
     * 查询指定类型的反馈列表
     */
    @Override
    public Result<List<Feedback>> getFeedbackByType(String type) {
        LambdaQueryWrapper<Feedback> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(Feedback::getType, type);
        
        List<Feedback> list = feedbackMapper.selectList(queryWrapper);
        log.info("查询类型为 {} 的反馈成功，数量: {}", type, list.size());
        return Result.ok(list);
    }

    /**
     * 更新反馈
     * 仅允许更新状态为"待处理"的反馈
     */
    public Result<Boolean> updateFeedback(Feedback feedback) {
        if (feedback.getId() == null) {
            return Result.fail("反馈ID不能为空");
        }
        
        // 先查询获取当前反馈的状态
        Feedback existing = feedbackMapper.selectById(feedback.getId());
        if (existing == null) {
            return Result.fail("反馈不存在");
        }
        
        // 仅允许状态为 0 (待处理) 的反馈进行修改
        if (existing.getStatus() != 0) {
            return Result.fail("该反馈已由管理员处理，无法修改");
        }
        
        // 更新允许修改的字段
        Feedback updateData = new Feedback();
        updateData.setId(feedback.getId());
        updateData.setType(feedback.getType());
        updateData.setContent(feedback.getContent());
        updateData.setContact(feedback.getContact());
        updateData.setImagesList(feedback.getImagesList());
        updateData.setUpdateTime(LocalDateTime.now());
        
        int rows = feedbackMapper.updateById(updateData);
        return rows > 0 ? Result.ok(true) : Result.fail("更新失败");
    }
}