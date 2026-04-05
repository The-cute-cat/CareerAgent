package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.service.SearchService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.naming.directory.SearchResult;
import java.util.List;

/**
 * SearchController
 * 搜索控制器
 * 用于处理搜索请求，支持关键词搜索功能
 * 主要功能：
 * 1. 根据关键词搜索相关内容
 * 2. 返回搜索结果列表
 * @module SearchController
 */
@Slf4j
@RestController
@RequestMapping("/search")
@RequiredArgsConstructor
public class SearchController {

    public final SearchService searchService;

    /**
     * search
     * 关键词搜索接口
     * 根据关键词搜索相关内容
     *
     * @param keyword 搜索关键词
     * @return 搜索结果列表
     * @todo 暂时定义为 List<Object>，后续根据需求修改
     */
    @GetMapping("/{keyword}")
    public Result<List<Object>> search(@PathVariable String keyword) {
        return searchService.search(keyword);
    }
}
