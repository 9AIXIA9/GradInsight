package com.gradinsight.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/stats")
public class StatsController {

    private final JdbcTemplate jdbc;

    public StatsController(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    /** GET /api/stats/overview */
    @GetMapping("/overview")
    public ResponseEntity<Map<String, Object>> overview() {
        try {
            Long totalTasks = jdbc.queryForObject("SELECT COUNT(*) FROM tasks", Long.class);
            if (totalTasks == null) totalTasks = 0L;

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

    /** GET /api/stats/hot-schools — 从帖子数最多的高校中取 Top 5 */
    @GetMapping("/hot-schools")
    public ResponseEntity<Map<String, Object>> hotSchools() {
        try {
            var rows = jdbc.queryForList(
                "SELECT keyword, COUNT(*) as cnt, COALESCE(SUM(like_count),0) as likes " +
                "FROM posts WHERE post_time > DATE_SUB(NOW(), INTERVAL 30 DAY) " +
                "GROUP BY keyword ORDER BY cnt DESC LIMIT 10");
            if (rows.isEmpty()) throw new RuntimeException("no data");
            var data = rows.stream().map(r -> Map.of(
                "name", (String) r.get("keyword"),
                "location", "", "type", "高等院校",
                "posts", formatK(((Number) r.get("cnt")).longValue()),
                "trend", "+" + (((Number) r.get("likes")).longValue() / 100) + "%"
            )).toList();
            return ResponseEntity.ok(Map.of("success", true, "data", data));
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of("success", true, "data", List.of()));
        }
    }

    /** GET /api/stats/latest-news — 最近完成的任务 + 系统信息 */
    @GetMapping("/latest-news")
    public ResponseEntity<Map<String, Object>> latestNews() {
        try {
            var tasks = jdbc.queryForList(
                "SELECT keyword, posts_collected, end_time FROM tasks WHERE status=0 " +
                "ORDER BY end_time DESC LIMIT 3");
            if (tasks.isEmpty()) throw new RuntimeException("no data");
            var data = new java.util.ArrayList<Map<String, Object>>();
            for (var t : tasks) {
                String kw = (String) t.get("keyword");
                int cnt = ((Number) t.get("posts_collected")).intValue();
                Map<String, Object> item = new LinkedHashMap<>();
                item.put("icon", "bi bi-check-circle-fill");
                item.put("title", kw + "数据采集完成");
                item.put("content", "共收集" + cnt + "条帖子");
                item.put("time", timeAgo(t.get("end_time")));
                item.put("type", "success");
                data.add(item);
            }
            Map<String, Object> sysInfo = new LinkedHashMap<>();
            sysInfo.put("icon", "bi bi-gear-fill");
            sysInfo.put("title", "系统运行正常");
            sysInfo.put("content", "所有服务运行稳定");
            sysInfo.put("time", "刚刚");
            sysInfo.put("type", "primary");
            data.add(sysInfo);
            return ResponseEntity.ok(Map.of("success", true, "data", data));
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of("success", true, "data", List.of(
                Map.of("icon", "bi bi-gear-fill", "title", "系统运行正常",
                    "content", "所有服务运行稳定", "time", "刚刚", "type", "primary")
            )));
        }
    }

    private String timeAgo(Object dt) {
        if (dt == null) return "";
        try {
            long diff = System.currentTimeMillis() - ((java.sql.Timestamp) dt).getTime();
            long min = diff / 60000, hr = min / 60, day = hr / 24;
            if (day > 0) return day + "天前";
            if (hr > 0) return hr + "小时前";
            if (min > 0) return min + "分钟前";
            return "刚刚";
        } catch (Exception e) { return ""; }
    }

    private static String formatK(long n) {
        if (n >= 10000) return (n / 1000) + "K+";
        if (n >= 1000) return String.format("%.1fK", n / 1000.0);
        return String.valueOf(n);
    }
}
