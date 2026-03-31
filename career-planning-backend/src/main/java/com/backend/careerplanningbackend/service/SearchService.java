package com.backend.careerplanningbackend.service;

import com.backend.careerplanningbackend.domain.po.Result;

import java.util.List;

public interface SearchService {
    Result<List<Object>> search(String keyword);
}
