package com.gradinsight.backend.controller;

import com.gradinsight.backend.repository.TaskRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/stats")
public class StatsController {

    private final JdbcTemplate jdbc;
    private final TaskRepository taskRepository;

    public StatsController(JdbcTemplate jdbc, TaskRepository taskRepository) {
        this.jdbc = jdbc;
        this.taskRepository = taskRepository;
    }

    /** GET /api/stats/overview */
    @GetMapping("/overview")
    public ResponseEntity<Map<String, Object>> overview() {
        try {
            long totalTasks = taskRepository.count();

            Long totalPosts = jdbc.queryForObject(
                "SELECT COUNT(*) FROM posts", Long.class);
            Long totalComments = jdbc.queryForObject(
                "SELECT COUNT(*) FROM comments", Long.class);
            Long totalLikes = jdbc.queryForObject(
                "SELECT COALESCE(SUM(like_count),0) FROM posts", Long.class);
            Long totalSchools = jdbc.queryForObject(
                "SELECT COUNT(DISTINCT keyword) FROM tasks", Long.class);

            return ResponseEntity.ok(Map.of(
                "success", true,
                "data", Map.of(
                    "totalPosts", formatK(totalPosts != null ? totalPosts : 0),
                    "totalComments", formatK(totalComments != null ? totalComments : 0),
                    "totalSchools", String.valueOf(totalSchools != null ? totalSchools : 0),
                    "totalTasks", String.valueOf(totalTasks),
                    "activeUsers", "1",
                    "totalLikes", formatK(totalLikes != null ? totalLikes : 0)
                )
            ));
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of(
                "success", true,
                "data", Map.of(
                    "totalPosts", "0", "totalComments", "0",
                    "totalSchools", "0", "totalTasks", "0",
                    "activeUsers", "0", "totalLikes", "0"
                )
            ));
        }
    }

    /** GET /api/stats/hot-schools */
    @GetMapping("/hot-schools")
    public ResponseEntity<Map<String, Object>> hotSchools() {
        return ResponseEntity.ok(Map.of(
            "success", true,
            "data", List.of(
                Map.of("name", "南昌大学", "location", "江西南昌", "type", "综合性大学", "posts", "1,234", "trend", "+15%"),
                Map.of("name", "华中科技大学", "location", "湖北武汉", "type", "理工类", "posts", "1,156", "trend", "+12%"),
                Map.of("name", "中南大学", "location", "湖南长沙", "type", "综合性大学", "posts", "1,087", "trend", "+18%"),
                Map.of("name", "西安交通大学", "location", "陕西西安", "type", "理工类", "posts", "987", "trend", "+10%"),
                Map.of("name", "湖南大学", "location", "湖南长沙", "type", "综合性大学", "posts", "876", "trend", "+8%")
            )
        ));
    }

    /** GET /api/stats/latest-news */
    @GetMapping("/latest-news")
    public ResponseEntity<Map<String, Object>> latestNews() {
        return ResponseEntity.ok(Map.of(
            "success", true,
            "data", List.of(
                Map.of("icon", "bi bi-check-circle-fill", "title", "数据采集完成",
                    "content", "南昌大学相关数据采集任务完成", "time", "2小时前", "type", "success"),
                Map.of("icon", "bi bi-rocket-fill", "title", "新任务启动",
                    "content", "计算机科学专业数据采集任务已启动", "time", "4小时前", "type", "primary"),
                Map.of("icon", "bi bi-bar-chart-fill", "title", "分析报告生成",
                    "content", "高校热度分析报告已生成", "time", "6小时前", "type", "info"),
                Map.of("icon", "bi bi-gear-fill", "title", "系统运行正常",
                    "content", "爬虫系统运行稳定，所有服务正常", "time", "1天前", "type", "warning")
            )
        ));
    }

    private static String formatK(long n) {
        if (n >= 10000) return (n / 1000) + "K+";
        if (n >= 1000) return String.format("%.1fK", n / 1000.0);
        return String.valueOf(n);
    }
}
