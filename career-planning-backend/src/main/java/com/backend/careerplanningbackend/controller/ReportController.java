package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.util.AiServiceClient;
import com.backend.careerplanningbackend.util.ThreadLocalUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * ReportController
 * 报告辅助控制器
 * 用于调用 AI 端（Python）的报告相关功能
 * 主要功能：
 * 1. 成长计划生成
 * 2. 报告完整性检查
 * 3. 段落智能润色
 */
@Slf4j
@RestController
@RequestMapping("/report")
@RequiredArgsConstructor
public class ReportController {

    private final AiServiceClient aiServiceClient;

    /**
     * 获取成长计划
     *
     * @param jobId        岗位 ID
     * @param cacheEnabled 是否启用缓存
     * @return 成长计划结果
     */
    @PostMapping("/plan")
    public Result<Object> getPlan(
            @RequestParam(value = "job_id") Integer jobId,
            @RequestParam(value = "cache_enabled", defaultValue = "true") Boolean cacheEnabled
    ) {
        try {
            Long userId = ThreadLocalUtil.getCurrentUserId();
            Map<String, Object> params = new HashMap<>();
            params.put("job_id", jobId);
            params.put("user_id", userId);
            params.put("cache_enabled", cacheEnabled);
            log.info("获取成长计划请求: userId={}, jobId={}, cacheEnabled={}", userId, jobId, cacheEnabled);
            AiChatResponse response = aiServiceClient.chatWithOther("/report/plan", params, true);
            if (response.isState()) {
                log.info("成长计划生成成功");
                return Result.ok(response.getData());
            } else {
                log.warn("成长计划生成失败: {}", response.getMsg());
                return Result.fail(response.getMsg());
            }
        } catch (Exception e) {
            log.error("调用成长计划服务失败", e);
            return Result.fail("调用成长计划服务失败: " + e.getMessage());
        }
    }

    /**
     * 报告完整性检查
     * 检查职业规划报告的完整性，包括：
     * 1. 人岗匹配四维度量化分析
     * 2. 职业发展路径规划
     * 3. 分阶段行动计划
     * 4. 评估周期与指标
     *
     * @param requestBody 请求体，包含 report_content, job_title
     * @return 检查结果
     */
    @PostMapping("/check")
    public Result<Object> checkReportIntegrity(@RequestBody Map<String, Object> requestBody) {
        try {
            String reportContent = (String) requestBody.get("report_content");
            String jobTitle = (String) requestBody.get("job_title");
            if (reportContent == null || reportContent.trim().length() < 50) {
                return Result.fail("报告内容过短，至少需要50个字符");
            }
            Long userId = ThreadLocalUtil.getCurrentUserId();
            log.info("报告完整性检查请求 | 用户: {} | 岗位: {}", userId, jobTitle != null ? jobTitle : "未指定");
            Map<String, Object> params = new HashMap<>();
            params.put("user_id", userId);
            params.put("report_content", reportContent);
            if (jobTitle != null) {
                params.put("job_title", jobTitle);
            }
            AiChatResponse response = aiServiceClient.chatWithOtherJson("/report/check", params, true);
            if (response.isState()) {
                log.info("报告完整性检查完成");
                return Result.ok(response.getData());
            } else {
                log.warn("报告完整性检查失败: {}", response.getMsg());
                return Result.fail(response.getMsg());
            }
        } catch (Exception e) {
            log.error("调用报告完整性检查服务失败", e);
            return Result.fail("检查失败：" + e.getMessage());
        }
    }

    /**
     * 段落智能润色
     * 根据报告类型动态切换润色策略：
     * - match_analysis：人岗匹配分析润色
     * - action_plan：行动计划润色
     * - other：通用润色
     *
     * @param requestBody 请求体，包含 original_content, report_type, context
     * @return 润色结果
     */
    @PostMapping("/polish")
    public Result<Object> polishParagraph(@RequestBody Map<String, Object> requestBody) {
        try {
            String originalContent = (String) requestBody.get("original_content");
            String reportType = (String) requestBody.get("report_type");
            @SuppressWarnings("unchecked")
            Map<String, Object> context = (Map<String, Object>) requestBody.get("context");

            // 验证报告类型
            if (reportType == null || (!reportType.equals("match_analysis") && !reportType.equals("action_plan") && !reportType.equals("other"))) {
                return Result.fail("无效的报告类型，有效值为：match_analysis, action_plan, other");
            }
            if (originalContent == null || originalContent.trim().length() < 20) {
                return Result.fail("原始内容过短，至少需要20个字符");
            }
            log.info("段落润色请求 | 类型: {}", reportType);

            Map<String, Object> params = new HashMap<>();
            params.put("original_content", originalContent);
            params.put("report_type", reportType);
            if (context != null) {
                params.put("context", context);
            }

            AiChatResponse response = aiServiceClient.chatWithOtherJson("/report/polish", params, true);
            if (response.isState()) {
                log.info("段落润色完成 | 类型: {}", reportType);
                return Result.ok(response.getData());
            } else {
                log.warn("段落润色失败: {}", response.getMsg());
                return Result.fail(response.getMsg());
            }
        } catch (Exception e) {
            log.error("调用段落润色服务失败", e);
            return Result.fail("润色失败：" + e.getMessage());
        }
    }
}
