package com.gradinsight.backend.controller;

import com.gradinsight.backend.grpc.CrawlerGrpcClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/crawler")
public class CrawlerController {
    private static final Logger log = LoggerFactory.getLogger(CrawlerController.class);

    private final JdbcTemplate jdbc;
    private final CrawlerGrpcClient crawlerGrpcClient;

    public CrawlerController(JdbcTemplate jdbc, CrawlerGrpcClient crawlerGrpcClient) {
        this.jdbc = jdbc;
        this.crawlerGrpcClient = crawlerGrpcClient;
    }

    /** POST /api/crawler/start — 直接调 Go gRPC，不创建冗余 Java Task */
    @PostMapping("/start")
    public ResponseEntity<Map<String, Object>> startCrawl(@RequestBody Map<String, Object> body) {
        try {
            String keyword = (String) body.getOrDefault("keyword", "");
            int site = body.get("site") instanceof Number ? ((Number) body.get("site")).intValue() : 0;
            int postCount = body.get("post_count") instanceof Number ? ((Number) body.get("post_count")).intValue() : 10;
            int minLikes = body.get("min_likes") instanceof Number ? ((Number) body.get("min_likes")).intValue() : 0;
            int commentsPerPost = body.get("comments_per_post") instanceof Number ? ((Number) body.get("comments_per_post")).intValue() : 10;
            int commentMinLikes = body.get("comment_min_likes") instanceof Number ? ((Number) body.get("comment_min_likes")).intValue() : 5;
            boolean includeComments = !Boolean.FALSE.equals(body.get("include_comments"));
            boolean includeImages = Boolean.TRUE.equals(body.get("include_images"));

            crawler.CrawlRequest req = crawler.CrawlRequest.newBuilder()
                    .setSite(crawler.Site.forNumber(site))
                    .setKeyword(keyword)
                    .setPostCount(postCount)
                    .setMinLikes(minLikes)
                    .setCommentsPerPost(commentsPerPost)
                    .setCommentMinLikes(commentMinLikes)
                    .setIncludeComments(includeComments)
                    .setIncludeImages(includeImages)
                    .build();

            crawler.CrawlResponse resp = crawlerGrpcClient.startCrawl(req);

            return ResponseEntity.ok(Map.of(
                    "task_id", resp.getTaskId(),
                    "success", resp.getSuccess(),
                    "message", resp.getMessage()
            ));
        } catch (Exception e) {
            log.error("startCrawl failed", e);
            return ResponseEntity.internalServerError().body(Map.of(
                    "task_id", "",
                    "success", false,
                    "message", e.getMessage()
            ));
        }
    }

    /** GET /api/crawler/tasks — 直接读 DB，不依赖 JPA entity */
    @GetMapping("/tasks")
    public ResponseEntity<Map<String, Object>> listTasks(
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "20") int limit,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String keyword) {
        limit = Math.min(limit, 100);

        var params = new ArrayList<Object>();
        var conditions = new ArrayList<String>();
        if (status != null && !status.isBlank()) {
            conditions.add("status = ?");
            params.add(Integer.parseInt(status));
        }
        if (keyword != null && !keyword.isBlank()) {
            conditions.add("keyword LIKE ?");
            params.add("%" + keyword + "%");
        }
        String where = conditions.isEmpty() ? "" : " WHERE " + String.join(" AND ", conditions);

        Long total = jdbc.queryForObject("SELECT COUNT(*) FROM tasks" + where, Long.class, params.toArray());
        if (total == null) total = 0L;

        var queryParams = new ArrayList<>(params);
        queryParams.add(limit);
        queryParams.add(skip);

        List<Map<String, Object>> rows = jdbc.queryForList(
            "SELECT * FROM tasks" + where + " ORDER BY created_at DESC LIMIT ? OFFSET ?",
            queryParams.toArray());

        List<Map<String, Object>> tasks = rows.stream().map(row -> {
            Map<String, Object> t = new LinkedHashMap<>();
            t.put("id", row.get("id"));
            t.put("task_id", row.get("id"));
            t.put("keyword", row.get("keyword"));
            t.put("site", row.get("site"));
            t.put("status", row.get("status"));
            t.put("posts_collected", row.get("posts_collected"));
            t.put("post_count", row.get("post_count"));
            t.put("created_at", row.get("created_at"));
            t.put("completed_at", row.get("end_time"));
            t.put("updated_at", row.get("updated_at"));
            t.put("error_message", row.get("error_msg"));
            t.put("include_comments", row.get("include_comments"));
            t.put("include_images", row.get("include_images"));
            return t;
        }).toList();

        return ResponseEntity.ok(Map.of("tasks", tasks, "total", total.intValue()));
    }

    /** GET /api/crawler/tasks/{taskId} */
    @GetMapping("/tasks/{taskId}")
    public ResponseEntity<?> getTask(@PathVariable String taskId) {
        var rows = jdbc.queryForList("SELECT * FROM tasks WHERE id = ?", taskId);
        if (rows.isEmpty()) return ResponseEntity.notFound().build();
        var row = rows.get(0);
        Map<String, Object> t = new LinkedHashMap<>();
        t.put("id", row.get("id"));
        t.put("task_id", row.get("id"));
        t.put("keyword", row.get("keyword"));
        t.put("site", row.get("site"));
        t.put("status", row.get("status"));
        t.put("posts_collected", row.get("posts_collected"));
        t.put("post_count", row.get("post_count"));
        t.put("created_at", row.get("created_at"));
        t.put("completed_at", row.get("end_time"));
        t.put("updated_at", row.get("updated_at"));
        t.put("error_message", row.get("error_msg"));
        return ResponseEntity.ok(t);
    }

    /** DELETE /api/crawler/tasks/{taskId} */
    @DeleteMapping("/tasks/{taskId}")
    public ResponseEntity<?> deleteTask(@PathVariable String taskId) {
        int n = jdbc.update("DELETE FROM tasks WHERE id = ?", taskId);
        if (n == 0) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(Map.of("message", "task deleted"));
    }

    /** POST /api/crawler/tasks/{taskId}/stop */
    @PostMapping("/tasks/{taskId}/stop")
    public ResponseEntity<?> stopTask(@PathVariable String taskId) {
        int n = jdbc.update("UPDATE tasks SET status = 4 WHERE id = ?", taskId);
        if (n == 0) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(Map.of("success", true, "message", "task stopped"));
    }

    /** GET /api/crawler/status */
    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getStatus() {
        Long count = jdbc.queryForObject("SELECT COUNT(*) FROM tasks", Long.class);
        return ResponseEntity.ok(Map.of(
                "success", true, "status", "HEALTHY",
                "healthy_instances", 1, "taskCount", count != null ? count : 0));
    }
}
