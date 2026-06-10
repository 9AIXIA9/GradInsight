package com.gradinsight.backend.controller;

import org.springframework.http.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@RestController
@RequestMapping("/api/posts")
public class PostController {

    private final JdbcTemplate jdbc;
    private final RestTemplate restTemplate = new RestTemplate();

    public PostController(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    /** 图片代理：绕过小红书防盗链 */
    @GetMapping("/image-proxy")
    public ResponseEntity<byte[]> imageProxy(@RequestParam String url) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.set("Referer", "https://www.xiaohongshu.com/");
            headers.set("User-Agent", "Mozilla/5.0");
            var entity = new HttpEntity<>(headers);
            ResponseEntity<byte[]> resp = restTemplate.exchange(url, HttpMethod.GET, entity, byte[].class);
            return ResponseEntity.ok()
                    .contentType(MediaType.parseMediaType("image/webp"))
                    .body(resp.getBody());
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }

    /** GET /api/posts */
    @GetMapping
    public ResponseEntity<Map<String, Object>> list(
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "20") int limit,
            @RequestParam(required = false) String task_id,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String tag,
            @RequestParam(required = false) Integer min_likes,
            @RequestParam(required = false) Integer min_comments,
            @RequestParam(defaultValue = "time") String sort_by,
            @RequestParam(defaultValue = "desc") String sort_order) {

        limit = Math.min(limit, 100);
        String sortCol = switch (sort_by) {
            case "like_count" -> "like_count";
            case "comment_count" -> "comment_count";
            case "collect_count" -> "collect_count";
            case "hot_score" -> "hot_score";
            default -> "post_time";
        };
        String order = "desc".equalsIgnoreCase(sort_order) ? "DESC" : "ASC";

        // build WHERE
        var conditions = new ArrayList<String>();
        var params = new ArrayList<Object>();
        if (task_id != null && !task_id.isBlank()) {
            conditions.add("task_id = ?");
            params.add(task_id);
        }
        if (keyword != null && !keyword.isBlank()) {
            conditions.add("(title LIKE ? OR content LIKE ? OR poster LIKE ?)");
            String kw = "%" + keyword + "%";
            params.add(kw);
            params.add(kw);
            params.add(kw);
        }
        if (tag != null && !tag.isBlank()) {
            conditions.add("JSON_CONTAINS(tags, ?)");
            params.add("\"" + tag + "\"");
        }
        if (min_likes != null) {
            conditions.add("like_count >= ?");
            params.add(min_likes);
        }
        if (min_comments != null) {
            conditions.add("comment_count >= ?");
            params.add(min_comments);
        }
        String where = conditions.isEmpty() ? "" : " WHERE " + String.join(" AND ", conditions);

        // count
        Long total = jdbc.queryForObject(
            "SELECT COUNT(*) FROM posts" + where, Long.class, params.toArray());

        // query posts
        String sql = "SELECT id, task_id, title, content, poster, post_time," +
            " like_count, comment_count, collect_count, location, tags, image_urls, link, hot_score" +
            " FROM posts" + where +
            " ORDER BY " + sortCol + " " + order +
            " LIMIT ? OFFSET ?";

        params.add(limit);
        params.add(skip);

        var posts = jdbc.queryForList(sql, params.toArray());

        // load comments for each post
        for (var post : posts) {
            String postId = (String) post.get("id");
            var comments = jdbc.queryForList(
                "SELECT id, commenter, content, comment_time, like_count, reply_count, location" +
                " FROM comments WHERE post_id = ? ORDER BY comment_time DESC LIMIT 20",
                postId);
            // rename columns for frontend
            var mapped = comments.stream().map(c -> {
                Map<String, Object> m = new LinkedHashMap<>();
                m.put("id", c.get("id"));
                m.put("commenter", c.get("commenter"));
                m.put("content", c.get("content"));
                m.put("time", c.get("comment_time"));
                m.put("like_count", c.get("like_count"));
                m.put("reply_count", c.get("reply_count"));
                m.put("location", c.get("location"));
                return m;
            }).toList();
            post.put("comments", mapped);
            // fix time field name
            post.put("time", post.remove("post_time"));
            // parse JSON string fields
            parseJsonArray(post, "tags");
            parseJsonArray(post, "image_urls");
        }

        return ResponseEntity.ok(Map.of(
            "posts", posts,
            "total", total != null ? total.intValue() : 0,
            "page", skip / limit + 1,
            "page_size", limit
        ));
    }

    private final com.fasterxml.jackson.databind.ObjectMapper objectMapper =
            new com.fasterxml.jackson.databind.ObjectMapper();

    @SuppressWarnings("unchecked")
    private void parseJsonArray(Map<String, Object> row, String key) {
        Object val = row.get(key);
        if (val == null) { row.put(key, List.of()); return; }
        if (val instanceof List<?>) return; // already parsed
        String s = val.toString().trim();
        if (s.isEmpty() || "null".equals(s)) { row.put(key, List.of()); return; }
        try {
            row.put(key, objectMapper.readValue(s, List.class));
        } catch (Exception e) {
            // RETURN RAW STRING so frontend can JSON.parse it
        }
    }
}
