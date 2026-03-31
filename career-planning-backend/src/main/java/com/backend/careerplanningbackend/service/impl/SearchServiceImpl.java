package com.backend.careerplanningbackend.service.impl;

import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.mapper.SearchMapper;
import com.backend.careerplanningbackend.service.SearchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SearchServiceImpl implements SearchService {
    @Autowired
    public SearchMapper searchMapper;
    
    @Override
    public Result<List<Object>> search(String keyword) {
//        todo 目前仅仅是一个占位符，后续根据需求修改.搜索功能暂定
//        searchMapper.search(keyword);
        return null;
    }
}
