package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.po.Feedback;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.service.IFeedbackService;
import com.baomidou.mybatisplus.core.metadata.IPage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * FeedbackController
 * 用户反馈控制器
 * 处理与用户反馈相关的业务逻辑，包括新增反馈、查询反馈、管理员回复等
 * 主要功能：
 * 1. 用户提交反馈
 * 2. 分页查询所有反馈
 * 3. 查询用户反馈历史
 * 4. 查询反馈详情
 * 5. 管理员回复反馈
 * 6. 删除反馈
 * @module FeedbackController
 */
@Slf4j
@RestController
@RequestMapping("/feedback")
@RequiredArgsConstructor
public class FeedbackController {

    private final IFeedbackService feedbackService;

    /**
     * 提交反馈
     * 用户提交反馈信息，包括反馈内容、类型、邮箱、URL等
     *
     * @param feedback 反馈信息
     * @return 操作结果
     */
    @PostMapping("/submit")
    public Result<Boolean> submitFeedback(@RequestBody Feedback feedback) {
        log.info("提交反馈: {}", feedback);
        return feedbackService.submitFeedback(feedback);
    }

    /**
     * 查询反馈列表（分页）
     * 支持按反馈类型筛选
     *
     * @param pageNum 页码
     * @param pageSize 每页数量
     * @param type 反馈类型（可选）
     * @return 分页结果
     */
    @GetMapping("/list")
    public Result<IPage<Feedback>> getFeedbackList(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String type) {
        log.info("查询反馈列表，页码: {}, 每页数量: {}, 类型: {}", pageNum, pageSize, type);
        return feedbackService.getFeedbackList(pageNum, pageSize, type);
    }

    /**
     * 查询用户反馈历史
     *
     * @param userId 用户ID
     * @param pageNum 页码
     * @param pageSize 每页数量
     * @return 用户反馈历史
     */
    @GetMapping("/user/{userId}/history")
    public Result<IPage<Feedback>> getUserFeedbackHistory(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize) {
        log.info("查询用户 {} 的反馈历史，页码: {}, 每页数量: {}", userId, pageNum, pageSize);
        return feedbackService.getUserFeedbackHistory(userId, pageNum, pageSize);
    }

    /**
     * 查询反馈详情
     *
     * @param id 反馈ID
     * @return 反馈详情
     */
    @GetMapping("/{id}")
    public Result<Feedback> getFeedbackById(@PathVariable Integer id) {
        log.info("查询反馈详情，ID: {}", id);
        return feedbackService.getFeedbackById(id);
    }

    /**
     * 管理员回复反馈
     *
     * @param id 反馈ID
     * @param response 回复内容
     * @return 操作结果
     */
    @PostMapping("/{id}/reply")
    public Result<Boolean> replyFeedback(
            @PathVariable Integer id,
            @RequestParam String response) {
        log.info("管理员回复反馈，ID: {}, 回复: {}", id, response);
        return feedbackService.replyFeedback(id, response);
    }

    /**
     * 删除反馈
     *
     * @param id 反馈ID
     * @return 操作结果
     */
    @DeleteMapping("/{id}")
    public Result<Boolean> deleteFeedback(@PathVariable Integer id) {
        log.info("删除反馈，ID: {}", id);
        return feedbackService.deleteFeedback(id);
    }

    /**
     * 查询指定类型的反馈
     *
     * @param type 反馈类型
     * @return 反馈列表
     */
    @GetMapping("/type/{type}")
    public Result<List<Feedback>> getFeedbackByType(@PathVariable String type) {
        log.info("查询类型为 {} 的反馈", type);
        return feedbackService.getFeedbackByType(type);
    }
}