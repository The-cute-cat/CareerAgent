package com.backend.careerplanningbackend.mapper;

import com.backend.careerplanningbackend.domain.po.Feedback;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper; 

@Mapper
public interface FeedbackMapper extends BaseMapper<Feedback> {
}