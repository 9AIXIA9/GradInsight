package com.gradinsight.backend.controller;

import com.gradinsight.proto.analysis.AnalyzeResponse;
import com.gradinsight.backend.service.AnalysisService;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
public class AnalysisController {

    private final AnalysisService analysisService;
    private final JdbcTemplate jdbc;

    public AnalysisController(AnalysisService analysisService, JdbcTemplate jdbc) {
        this.analysisService = analysisService;
        this.jdbc = jdbc;
    }

    @PostMapping("/analysis/analyze")
    public ResponseEntity<Map<String, Object>> analyze(@RequestBody Map<String, Object> body) {
        @SuppressWarnings("unchecked")
        List<String> types = (List<String>) body.getOrDefault("analysis_types", List.of());
        String keyword = (String) body.getOrDefault("keyword_filter", null);
        int minPosts = body.get("min_posts") instanceof Number ? ((Number) body.get("min_posts")).intValue() : 5;

        AnalyzeResponse resp = analysisService.analyze(types, keyword, minPosts);
        return ResponseEntity.ok(Map.of(
                "success", resp.getSuccess(),
                "message", resp.getMessage(),
                "analysis_id", resp.getData().getAnalysisId()
        ));
    }

    // ===== 查询（Java 直读 MySQL）=====

    @GetMapping("/analysis/history")
    public ResponseEntity<Map<String, Object>> history(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int pageSize) {
        int offset = (page - 1) * pageSize;
        Long total = jdbc.queryForObject("SELECT COUNT(*) FROM content_analysis_results", Long.class);
        var rows = jdbc.queryForList(
                "SELECT id, task_id, analysis_type, total_posts_analyzed, processing_time, created_at " +
                "FROM content_analysis_results ORDER BY created_at DESC LIMIT ? OFFSET ?",
                pageSize, offset);
        List<Map<String, Object>> analyses = rows.stream().map(row -> {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("analysis_id", row.get("id"));
            m.put("task_id", row.get("task_id"));
            m.put("analysis_type", row.get("analysis_type"));
            m.put("total_posts_analyzed", row.get("total_posts_analyzed"));
            m.put("processing_time", row.get("processing_time"));
            m.put("created_at", row.get("created_at"));
            return m;
        }).toList();
        return ResponseEntity.ok(Map.of(
                "success", true,
                "data", Map.of("analyses", analyses, "total", total != null ? total : 0,
                        "page", page, "page_size", pageSize)
        ));
    }

    @GetMapping("/analysis/types")
    public ResponseEntity<Map<String, Object>> types() {
        var types = List.of(
                Map.of("type", "topic_summary", "name", "话题总结"),
                Map.of("type", "content_clustering", "name", "内容聚类"),
                Map.of("type", "keyword_extraction", "name", "关键词提取"),
                Map.of("type", "sentiment_analysis", "name", "情感分析"),
                Map.of("type", "university_mention", "name", "高校提及分析"),
                Map.of("type", "major_analysis", "name", "专业分析")
        );
        return ResponseEntity.ok(Map.of("success", true, "data", types));
    }

    @GetMapping("/analysis/{analysisId}")
    public ResponseEntity<Map<String, Object>> detail(@PathVariable String analysisId) {
        var rows = jdbc.queryForList(
                "SELECT * FROM content_analysis_results WHERE id = ?", analysisId);
        if (rows.isEmpty()) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(Map.of("success", true, "data", rows.get(0)));
    }

    @DeleteMapping("/analysis/{analysisId}")
    public ResponseEntity<Map<String, Object>> delete(@PathVariable String analysisId) {
        jdbc.update("DELETE FROM content_analysis_results WHERE id = ?", analysisId);
        return ResponseEntity.ok(Map.of("success", true, "message", "deleted"));
    }
}
