package com.backend.careerplanningbackend.service.impl;

import com.backend.careerplanningbackend.domain.po.PointsTransaction;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.mapper.PointsTransactionMapper;
import com.backend.careerplanningbackend.service.TransactionService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

@Slf4j
@RequiredArgsConstructor
@Service
public class TransactionServiceImpl implements TransactionService {
    
    private final PointsTransactionMapper pointsTransactionMapper;
    @Override
    public Result<PointsTransaction> getTransaction(Long userId) {
        PointsTransaction pointsTransaction = pointsTransactionMapper.selectOne(new LambdaQueryWrapper<PointsTransaction>()
                .eq(PointsTransaction::getUserId, userId)
        );
        return Result.ok(pointsTransaction);
    }

    @Override
    public Result<List<PointsTransaction>> getTransactionList(Long userId) {
        return null;
    }

    @Override
    public Result<List<PointsTransaction>> getTransactionListPoints() {
        return null;
    }

    @Override
    public Result<List<PointsTransaction>> getTransactionListMember() {
        return null;
    }
}
