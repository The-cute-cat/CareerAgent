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
        try {
            Long currentUserId = ThreadLocalUtil.getCurrentUserId();
            feedback.setUserId(currentUserId);
            
            boolean success = feedbackMapper.insert(feedback) > 0;
            if (success) {
                log.info("用户 {} 提交反馈成功，反馈类型: {}", currentUserId, feedback.getType());
                return Result.ok(true);
            } else {
                log.error("用户 {} 提交反馈失败", currentUserId);
                return Result.fail("反馈提交失败");
            }
        } catch (Exception e) {
            log.error("FeedbackServiceImpl.submitFeedback 提交反馈异常", e);
            return Result.fail("反馈提交异常: " + e.getMessage());
        }
    }

    /**
     * 分页查询所有反馈（支持多条件筛选）
     */
    public Result<IPage<Feedback>> getFeedbackList(Integer pageNum, Integer pageSize, String type) {
        try {
            Page<Feedback> page = new Page<>(pageNum, pageSize);
            
            LambdaQueryWrapper<Feedback> queryWrapper = new LambdaQueryWrapper<>();
            if (type != null && !type.isEmpty()) {
                queryWrapper.eq(Feedback::getType, type);
            }
            
            IPage<Feedback> result = feedbackMapper.selectPage(page, queryWrapper);
            log.info("分页查询反馈成功，页码: {}, 每页数量: {}, 总数: {}", pageNum, pageSize, result.getTotal());
            return Result.ok(result);
        } catch (Exception e) {
            log.error("FeedbackServiceImpl.getFeedbackList 分页查询反馈异常", e);
            return Result.fail("查询反馈失败");
        }
    }

    /**
     * 查询用户的反馈历史
     */
    public Result<IPage<Feedback>> getUserFeedbackHistory(Long userId, Integer pageNum, Integer pageSize) {
        try {
            Page<Feedback> page = new Page<>(pageNum, pageSize);
            
            LambdaQueryWrapper<Feedback> queryWrapper = new LambdaQueryWrapper<>();
            queryWrapper.eq(Feedback::getUserId, userId)
                    .orderByDesc(Feedback::getId);
            
            IPage<Feedback> result = feedbackMapper.selectPage(page, queryWrapper);
            log.info("查询用户 {} 的反馈历史成功，总数: {}", userId, result.getTotal());
            return Result.ok(result);
        } catch (Exception e) {
            log.error("FeedbackServiceImpl.getUserFeedbackHistory 查询用户反馈历史异常, 用户ID: {}", userId, e);
            return Result.fail("查询反馈历史失败");
        }
    }

    /**
     * 获取反馈详情
     */
    public Result<Feedback> getFeedbackById(Integer id) {
        try {
            Feedback feedback = feedbackMapper.selectById(id);
            if (feedback != null) {
                log.info("查询反馈详情成功，反馈ID: {}", id);
                return Result.ok(feedback);
            } else {
                log.warn("反馈不存在，反馈ID: {}", id);
                return Result.fail("反馈不存在");
            }
        } catch (Exception e) {
            log.error("FeedbackServiceImpl.getFeedbackById 查询反馈详情异常, 反馈ID: {}", id, e);
            return Result.fail("查询反馈详情失败");
        }
    }

    /**
     * 管理员回复反馈
     */
    @Transactional(rollbackFor = Exception.class)
    public Result<Boolean> replyFeedback(Integer id, String response) {
        try {
            Feedback feedback = feedbackMapper.selectById(id);
            if (feedback == null) {
                log.warn("反馈不存在，无法回复，反馈ID: {}", id);
                return Result.fail("反馈不存在");
            }
            
            feedback.setResponse(response);
            boolean success = feedbackMapper.updateById(feedback) > 0;
            if (success) {
                log.info("管理员回复反馈成功，反馈ID: {}", id);
                return Result.ok(true);
            } else {
                log.error("管理员回复反馈失败，反馈ID: {}", id);
                return Result.fail("回复失败");
            }
        } catch (Exception e) {
            log.error("FeedbackServiceImpl.replyFeedback 管理员回复反馈异常, 反馈ID: {}", id, e);
            return Result.fail("回复失败: " + e.getMessage());
        }
    }

    /**
     * 删除反馈
     */
    @Transactional(rollbackFor = Exception.class)
    public Result<Boolean> deleteFeedback(Integer id) {
        try {
            boolean success = feedbackMapper.deleteById(id) > 0;
            if (success) {
                log.info("删除反馈成功，反馈ID: {}", id);
                return Result.ok(true);
            } else {
                log.error("删除反馈失败，反馈ID: {}", id);
                return Result.fail("删除失败");
            }
        } catch (Exception e) {
            log.error("FeedbackServiceImpl.deleteFeedback 删除反馈异常, 反馈ID: {}", id, e);
            return Result.fail("删除失败: " + e.getMessage());
        }
    }

    /**
     * 查询指定类型的反馈列表
     */
    @Override
    public Result<List<Feedback>> getFeedbackByType(String type) {
        try {
            LambdaQueryWrapper<Feedback> queryWrapper = new LambdaQueryWrapper<>();
            queryWrapper.eq(Feedback::getType, type);
            
            List<Feedback> list = feedbackMapper.selectList(queryWrapper);
            log.info("查询类型为 {} 的反馈成功，数量: {}", type, list.size());
            return Result.ok(list);
        } catch (Exception e) {
            log.error("FeedbackServiceImpl.getFeedbackByType 查询指定类型反馈异常, 类型: {}", type, e);
            return Result.fail("查询失败");
        }
    }

    @Override
    public Result<Boolean> updateFeedback(Feedback feedback) {
        if (feedback.getId() == null) {
            return Result.fail("反馈ID不能为空");
        }
        
        Feedback existing = feedbackMapper.selectById(feedback.getId());
        if (existing == null) {
            return Result.fail("反馈不存在");
        }
        
        // 仅允许状态为 0 (待处理) 的反馈进行修改
        if (existing.getStatus() != 0) {
            return Result.fail("该反馈已由管理员处理，无法修改");
        }
        
        try {
            // 更新允许修改的字段
            existing.setType(feedback.getType());
            existing.setContent(feedback.getContent());
            existing.setContact(feedback.getContact());
            existing.setImagesList(feedback.getImagesList());
            existing.setUpdateTime(LocalDateTime.now());
            
            int rows = feedbackMapper.updateById(existing);
            return rows > 0 ? Result.ok(true) : Result.fail("更新失败");
        } catch (Exception e) {
            log.error("FeedbackServiceImpl.updateFeedback 更新反馈异常, 反馈ID: {}", feedback.getId(), e);
            return Result.fail("更新失败: " + e.getMessage());
        }
    }
}