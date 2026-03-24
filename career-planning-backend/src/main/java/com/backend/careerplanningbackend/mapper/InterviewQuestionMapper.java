package com.backend.careerplanningbackend.mapper;

import com.backend.careerplanningbackend.domain.po.InterviewQuestion;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/**
 * 八股文问答 Mapper
 */
@Mapper
public interface InterviewQuestionMapper extends BaseMapper<InterviewQuestion> {
}

