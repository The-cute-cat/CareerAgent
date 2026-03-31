package com.backend.careerplanningbackend.service;

import com.backend.careerplanningbackend.domain.po.PointsTransaction;
import com.backend.careerplanningbackend.domain.po.Result;

import java.util.List;

public interface TransactionService {
    Result<PointsTransaction> getTransaction(Long userId);

    Result<List<PointsTransaction>> getTransactionList(Long userId);

    Result<List<PointsTransaction>> getTransactionListPoints();

    Result<List<PointsTransaction>> getTransactionListMember();
}
