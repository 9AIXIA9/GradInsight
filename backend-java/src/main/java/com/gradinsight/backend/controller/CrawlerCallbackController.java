package com.gradinsight.backend.controller;

import com.gradinsight.backend.service.TaskService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/crawler")
public class CrawlerCallbackController {
    private static final Logger log = LoggerFactory.getLogger(CrawlerCallbackController.class);

    private final TaskService taskService;

    public CrawlerCallbackController(TaskService taskService) {
        this.taskService = taskService;
    }

    @PostMapping("/callback")
    public ResponseEntity<?> callback(@RequestBody Map<String, Object> payload) {
        try {
            // 支持多种命名风格
            String crawlerTaskId = payload.containsKey("crawler_task_id") ? (String) payload.get("crawler_task_id") : (String) payload.get("crawlerTaskId");
            String id = payload.containsKey("id") ? String.valueOf(payload.get("id")) : (String) payload.get("task_id");

            Integer postsCollected = null;
            if (payload.containsKey("posts_collected")) postsCollected = ((Number) payload.get("posts_collected")).intValue();
            else if (payload.containsKey("postsCollected")) postsCollected = ((Number) payload.get("postsCollected")).intValue();

            String errorMsg = payload.containsKey("error_msg") ? (String) payload.get("error_msg") : (String) payload.get("errorMsg");

            // 状态：允许字符串或数字
            Integer status = null;
            Object statusObj = payload.get("status");
            if (statusObj instanceof Number) status = ((Number) statusObj).intValue();
            else if (statusObj instanceof String) {
                String s = ((String) statusObj).toLowerCase();
                if (s.contains("success") || s.contains("completed")) status = 0;
                else if (s.contains("fail") || s.contains("error")) status = 1;
                else if (s.contains("running")) status = 2;
            }

            String endTime = payload.containsKey("end_time") ? (String) payload.get("end_time") : (String) payload.get("endTime");

            var updated = taskService.applyCrawlerCallback(id, crawlerTaskId, status, postsCollected, errorMsg, endTime);
            if (updated == null) {
                log.warn("callback: task not found for payload: {}", payload);
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("success", false, "message", "task not found"));
            }

            log.info("callback: task updated {} -> status={}", updated.getId(), updated.getStatus());
            return ResponseEntity.ok(Map.of("success", true, "message", "task updated"));

        } catch (Exception ex) {
            log.error("callback handling failed", ex);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("success", false, "message", ex.getMessage()));
        }
    }
}
