package com.backend.careerplanningbackend.service.impl;

import com.backend.careerplanningbackend.domain.dto.PackageDTO;
import com.backend.careerplanningbackend.domain.po.Package;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.mapper.PackageMapper;
import com.backend.careerplanningbackend.service.PackageService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * PackageServiceImpl.java
 * 套餐业务逻辑实现类
 * 实现套餐的增删查改操作
 * 
 * @author Career Agent
 * @version 1.0
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class PackageServiceImpl implements PackageService {

    private final PackageMapper packageMapper;

    @Override
    @Transactional
    public Result<String> addPackage(PackageDTO packageDTO) {
        try {
            Package packagePo = new Package();
            BeanUtils.copyProperties(packageDTO, packagePo);
            
            // 默认新套餐为启用状态
            if (packagePo.getStatus() == null) {
                packagePo.setStatus(1);
            }
            
            int inserted = packageMapper.insert(packagePo);
            if (inserted > 0) {
                log.info("成功添加套餐: {}", packagePo);
                return Result.ok("套餐添加成功");
            } else {
                log.warn("套餐添加失败");
                return Result.fail("套餐添加失败");
            }
        } catch (Exception e) {
            log.error("添加套餐异常", e);
            return Result.fail("套餐添加异常: " + e.getMessage());
        }
    }

    @Override
    @Transactional
    public Result<String> deletePackage(Long id) {
        try {
            if (id == null || id <= 0) {
                return Result.fail("套餐ID不合法");
            }
            
            // 检查套餐是否存在
            Package packagePo = packageMapper.selectById(id);
            if (packagePo == null) {
                log.warn("套餐不存在，ID: {}", id);
                return Result.fail("套餐不存在");
            }
            
            int deleted = packageMapper.deleteById(id);
            if (deleted > 0) {
                log.info("成功删除套餐，ID: {}", id);
                return Result.ok("套餐删除成功");
            } else {
                log.warn("套餐删除失败，ID: {}", id);
                return Result.fail("套餐删除失败");
            }
        } catch (Exception e) {
            log.error("删除套餐异常", e);
            return Result.fail("套餐删除异常: " + e.getMessage());
        }
    }

    @Override
    @Transactional
    public Result<String> updatePackage(PackageDTO packageDTO) {
        try {
            if (packageDTO.getId() == null || packageDTO.getId() <= 0) {
                return Result.fail("套餐ID不合法");
            }
            
            // 检查套餐是否存在
            Package existingPackage = packageMapper.selectById(packageDTO.getId());
            if (existingPackage == null) {
                log.warn("套餐不存在，ID: {}", packageDTO.getId());
                return Result.fail("套餐不存在");
            }
            
            Package packagePo = new Package();
            BeanUtils.copyProperties(packageDTO, packagePo);
            
            int updated = packageMapper.updateById(packagePo);
            if (updated > 0) {
                log.info("成功更新套餐，ID: {}", packageDTO.getId());
                return Result.ok("套餐更新成功");
            } else {
                log.warn("套餐更新失败，ID: {}", packageDTO.getId());
                return Result.fail("套餐更新失败");
            }
        } catch (Exception e) {
            log.error("更新套餐异常", e);
            return Result.fail("套餐更新异常: " + e.getMessage());
        }
    }

    @Override
    public Result<Package> getPackageById(Long id) {
        try {
            if (id == null || id <= 0) {
                return Result.fail("套餐ID不合法");
            }
            
            Package packagePo = packageMapper.selectById(id);
            if (packagePo == null) {
                log.warn("套餐不存在，ID: {}", id);
                return Result.fail("套餐不存在");
            }
            
            return Result.ok(packagePo);
        } catch (Exception e) {
            log.error("查询套餐异常", e);
            return Result.fail("查询套餐异常: " + e.getMessage());
        }
    }

    @Override
    public Result<List<Package>> getAllPackages() {
        try {
            // 只查询启用的套餐
            List<Package> packages = packageMapper.selectList(
                    new LambdaQueryWrapper<Package>()
                            .eq(Package::getStatus, 1)
            );
            
            log.info("成功查询所有套餐，数量: {}", packages.size());
            return Result.ok(packages);
        } catch (Exception e) {
            log.error("查询套餐列表异常", e);
            return Result.fail("查询套餐列表异常: " + e.getMessage());
        }
    }

    @Override
    public Result<List<Package>> getPackagesByType(Integer type) {
        try {
            if (type == null || (type != 1 && type != 2)) {
                return Result.fail("套餐类型不合法");
            }
            
            List<Package> packages = packageMapper.selectList(
                    new LambdaQueryWrapper<Package>()
                            .eq(Package::getType, type)
                            .eq(Package::getStatus, 1)
            );
            
            log.info("成功查询类型为{}的套餐，数量: {}", type, packages.size());
            return Result.ok((List<Package>) (List<?>) packages);
        } catch (Exception e) {
            log.error("查询套餐列表异常", e);
            return Result.fail("查询套餐列表异常: " + e.getMessage());
        }
    }
}


