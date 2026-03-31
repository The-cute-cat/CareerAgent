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

@Slf4j
@RestController
@RequestMapping("/search")
@RequiredArgsConstructor
public class SearchController {
    
    public final SearchService searchService;
    
    //todo 暂时定义为 List<Object>, 后续根据需求修改
    @GetMapping("/{keyword}")
    public Result<List<Object>> search(@PathVariable String keyword) {
        return searchService.search(keyword);
    }
}
