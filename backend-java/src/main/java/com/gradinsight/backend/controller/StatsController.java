package com.gradinsight.backend.controller;

import com.gradinsight.backend.repository.TaskRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

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

            // completed tasks
            var statusCounts = jdbc.queryForList(
                "SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status");
            long completed = 0, failed = 0, running = 0;
            for (var row : statusCounts) {
                int s = ((Number) row.get("status")).intValue();
                long c = ((Number) row.get("cnt")).longValue();
                if (s == 0) completed = c;
                else if (s == 1) failed = c;
                else if (s == 2) running = c;
            }

            // total posts
            Long totalPosts = jdbc.queryForObject("SELECT COUNT(*) FROM posts", Long.class);
            Long totalComments = jdbc.queryForObject("SELECT COUNT(*) FROM comments", Long.class);
            Long totalLikes = jdbc.queryForObject(
                "SELECT COALESCE(SUM(like_count),0) FROM posts", Long.class);

            return ResponseEntity.ok(Map.of(
                "success", true,
                "data", Map.of(
                    "totalPosts", formatK(totalPosts != null ? totalPosts : 0),
                    "totalComments", formatK(totalComments != null ? totalComments : 0),
                    "totalSchools", String.valueOf(jdbc.queryForObject(
                        "SELECT COUNT(DISTINCT keyword) FROM tasks", Long.class)),
                    "totalTasks", String.valueOf(totalTasks),
                    "activeUsers", "1",
                    "totalLikes", formatK(totalLikes != null ? totalLikes : 0)
                )
            ));
        } catch (Exception e) {
            // 数据库视图可能不存在，返回默认值
            return ResponseEntity.ok(Map.of(
                "success", true,
                "data", Map.of(
                    "totalPosts", "0",
                    "totalComments", "0",
                    "totalSchools", "0",
                    "totalTasks", "0",
                    "activeUsers", "0",
                    "totalLikes", "0"
                )
            ));
        }
    }

    private static String formatK(long n) {
        if (n >= 10000) return (n / 1000) + "K+";
        if (n >= 1000) return String.format("%.1fK", n / 1000.0);
        return String.valueOf(n);
    }
}
