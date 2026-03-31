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

@Slf4j
@RestController
@RequestMapping("/transaction")
@RequiredArgsConstructor
public class TransactionController {
    
    private final TransactionService transactionService;
    
    @GetMapping("/{id}")
    public Result<PointsTransaction> getTransaction(Long userId) {
        return transactionService.getTransaction(userId);
    }
    
    @GetMapping("/list/{id}")
    public Result<List<PointsTransaction>> getTransactionList(Long userId) {
        return transactionService.getTransactionList(userId);
    }
    
    @GetMapping("/list/points/{id}")
    public Result<List<PointsTransaction>> getTransactionListPoints(Long userId) {
        return transactionService.getTransactionListPoints();
    }

    @GetMapping("/list/member/{id}")
    public Result<List<PointsTransaction>> getTransactionListMember(Long userId) {
        return transactionService.getTransactionListMember();
    }
}
