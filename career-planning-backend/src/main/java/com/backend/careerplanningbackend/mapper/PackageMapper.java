package com.backend.careerplanningbackend.mapper;

import com.backend.careerplanningbackend.domain.po.Package;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/**
 * PackageMapper.java
 * 套餐数据库操作接口
 * 继承 BaseMapper 获得基础的增删查改方法
 * 
 * @author Career Agent
 * @version 1.0
 */
@Mapper
public interface PackageMapper extends BaseMapper<Package> {
    
}

