package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.PackageDTO;
import com.backend.careerplanningbackend.domain.po.Package;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.service.PackageService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * PackageController.java
 * 套餐控制器
 * 处理与套餐相关的API接口
 * 主要功能：
 * 1. 套餐的增删查改操作
 * 2. 套餐列表查询（按类型、按状态）
 * 
 * @author Career Agent
 * @version 1.0
 */
@Slf4j
@RestController
@RequestMapping("/package")
@RequiredArgsConstructor
public class PackageController {

    private final PackageService packageService;

    /**
     * 添加套餐
     * 
     * @param packageDTO 套餐信息
     * @return 操作结果
     */
    @PostMapping("/add")
    public Result<String> addPackage(@Valid @RequestBody PackageDTO packageDTO) {
        log.info("收到添加套餐请求: {}", packageDTO);
        return packageService.addPackage(packageDTO);
    }

    /**
     * 删除套餐
     * 
     * @param id 套餐ID
     * @return 操作结果
     */
    @DeleteMapping("/delete/{id}")
    public Result<String> deletePackage(@PathVariable Long id) {
        log.info("收到删除套餐请求，套餐ID: {}", id);
        return packageService.deletePackage(id);
    }

    /**
     * 更新套餐
     * 
     * @param packageDTO 套餐信息
     * @return 操作结果
     */
    @PutMapping("/update")
    public Result<String> updatePackage(@Valid @RequestBody PackageDTO packageDTO) {
        log.info("收到更新套餐请求: {}", packageDTO);
        return packageService.updatePackage(packageDTO);
    }

    /**
     * 查询单个套餐
     * 
     * @param id 套餐ID
     * @return 套餐信息
     */
    @GetMapping("/{id}")
    public Result<Package> getPackageById(@PathVariable Long id) {
        log.info("收到查询套餐请求，套餐ID: {}", id);
        return packageService.getPackageById(id);
    }

    /**
     * 查询所有启用的套餐
     * 
     * @return 套餐列表
     */
    @GetMapping("/list/all")
    public Result<List<Package>> getAllPackages() {
        log.info("收到查询所有套餐请求");
        return packageService.getAllPackages();
    }

    /**
     * 按类型查询套餐
     * 
     * @param type 套餐类型（1-积分, 2-会员）
     * @return 套餐列表
     */
    @GetMapping("/list/type/{type}")
    public Result<List<Package>> getPackagesByType(@PathVariable Integer type) {
        log.info("收到按类型查询套餐请求，类型: {}", type);
        return packageService.getPackagesByType(type);
    }
}

