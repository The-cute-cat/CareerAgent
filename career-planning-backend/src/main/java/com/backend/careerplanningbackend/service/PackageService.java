package com.backend.careerplanningbackend.service;

import com.backend.careerplanningbackend.domain.dto.PackageDTO;
import com.backend.careerplanningbackend.domain.po.Package;
import com.backend.careerplanningbackend.domain.po.Result;

import java.util.List;

/**
 * PackageService.java
 * 套餐业务逻辑接口
 * 定义套餐相关的业务操作
 * 
 * @author Career Agent
 * @version 1.0
 */
public interface PackageService {
    
    /**
     * 添加套餐
     * @param packageDTO 套餐信息
     * @return 操作结果
     */
    Result<String> addPackage(PackageDTO packageDTO);
    
    /**
     * 删除套餐
     * @param id 套餐ID
     * @return 操作结果
     */
    Result<String> deletePackage(Long id);
    
    /**
     * 更新套餐
     * @param packageDTO 套餐信息
     * @return 操作结果
     */
    Result<String> updatePackage(PackageDTO packageDTO);
    
    /**
     * 查询单个套餐
     * @param id 套餐ID
     * @return 套餐信息
     */
    Result<Package> getPackageById(Long id);
    
    /**
     * 查询所有启用的套餐
     * @return 套餐列表
     */
    Result<List<Package>> getAllPackages();
    
    /**
     * 按类型查询套餐
     * @param type 套餐类型（1-积分, 2-会员）
     * @return 套餐列表
     */
    Result<List<Package>> getPackagesByType(Integer type);
}

