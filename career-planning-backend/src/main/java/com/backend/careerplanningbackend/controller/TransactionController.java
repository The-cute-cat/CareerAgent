package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.po.PointsTransaction;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.service.TransactionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * TransactionController
 * 交易记录控制器
 * 用于处理交易记录相关的查询请求
 * 主要功能：
 * 1. 查询单条交易记录
 * 2. 查询用户的所有交易记录
 * 3. 查询积分相关的交易记录
 * 4. 查询会员相关的交易记录
 * @module TransactionController
 */
@Slf4j
@RestController
@RequestMapping("/transaction")
@RequiredArgsConstructor
public class TransactionController {

    private final TransactionService transactionService;

    /**
     * getTransaction
     * 获取单条交易记录
     *
     * @param userId 用户 ID
     * @return 交易记录
     */
    @GetMapping("/{id}")
    public Result<PointsTransaction> getTransaction(Long userId) {
        return transactionService.getTransaction(userId);
    }

    /**
     * getTransactionList
     * 获取用户的所有交易记录
     *
     * @param userId 用户 ID
     * @return 交易记录列表
     */
    @GetMapping("/list/{id}")
    public Result<List<PointsTransaction>> getTransactionList(Long userId) {
        return transactionService.getTransactionList(userId);
    }

    /**
     * getTransactionListPoints
     * 获取积分相关的交易记录
     *
     * @param userId 用户 ID（未使用，待修复）
     * @return 积分交易记录列表
     */
    @GetMapping("/list/points/{id}")
    public Result<List<PointsTransaction>> getTransactionListPoints(Long userId) {
        return transactionService.getTransactionListPoints();
    }

    /**
     * getTransactionListMember
     * 获取会员相关的交易记录
     *
     * @param userId 用户 ID（未使用，待修复）
     * @return 会员交易记录列表
     */
    @GetMapping("/list/member/{id}")
    public Result<List<PointsTransaction>> getTransactionListMember(Long userId) {
        return transactionService.getTransactionListMember();
    }
}
