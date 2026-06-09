package com.gradinsight.backend.controller;

import com.gradinsight.backend.dto.TaskDTO;
import com.gradinsight.backend.entity.Task;
import com.gradinsight.backend.repository.TaskRepository;
import com.gradinsight.backend.service.CrawlerDispatchService;
import com.gradinsight.backend.service.TaskService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/crawler")
public class CrawlerController {
    private static final Logger log = LoggerFactory.getLogger(CrawlerController.class);

    private final TaskService taskService;
    private final TaskRepository taskRepository;
    private final CrawlerDispatchService dispatchService;

    public CrawlerController(TaskService taskService, TaskRepository taskRepository,
                             CrawlerDispatchService dispatchService) {
        this.taskService = taskService;
        this.taskRepository = taskRepository;
        this.dispatchService = dispatchService;
    }

    /** POST /api/crawler/start */
    @PostMapping("/start")
    public ResponseEntity<Map<String, Object>> startCrawl(@RequestBody Map<String, Object> body) {
        try {
            String keyword = (String) body.getOrDefault("keyword", "");
            Integer site = body.get("site") instanceof Number ? ((Number) body.get("site")).intValue() : 0;
            int postCount = body.get("post_count") instanceof Number ? ((Number) body.get("post_count")).intValue() : 10;
            int minLikes = body.get("min_likes") instanceof Number ? ((Number) body.get("min_likes")).intValue() : 0;
            int commentsPerPost = body.get("comments_per_post") instanceof Number ? ((Number) body.get("comments_per_post")).intValue() : 10;
            int commentMinLikes = body.get("comment_min_likes") instanceof Number ? ((Number) body.get("comment_min_likes")).intValue() : 5;
            boolean includeComments = !Boolean.FALSE.equals(body.get("include_comments"));
            boolean includeImages = Boolean.TRUE.equals(body.get("include_images"));

            Task task = new Task();
            task.setKeyword(keyword);
            task.setSite(site);
            task.setPostCount((long) postCount);
            task.setMinLikes((long) minLikes);
            task.setCommentsPerPost((long) commentsPerPost);
            task.setCommentMinLikes((long) commentMinLikes);
            task.setIncludeComments(includeComments);
            task.setIncludeImages(includeImages);
            task.setStatus(3); // pending

            Task saved = taskRepository.save(task);

            try {
                dispatchService.dispatch(saved);
            } catch (Exception ex) {
                log.warn("dispatch submit failed for {}: {}", saved.getId(), ex.getMessage());
            }

            return ResponseEntity.ok(Map.of(
                    "task_id", saved.getId(),
                    "success", true,
                    "message", "task created"
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

    /** GET /api/crawler/tasks */
    @GetMapping("/tasks")
    public ResponseEntity<Map<String, Object>> listTasks(
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "20") int limit,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String keyword) {

        List<Task> all = taskRepository.findAll();
        var filtered = all.stream().filter(t -> {
            if (status != null && !status.isBlank()) {
                try { if (t.getStatus() != Integer.parseInt(status)) return false; }
                catch (NumberFormatException ignored) {}
            }
            if (keyword != null && !keyword.isBlank()) {
                if (t.getKeyword() == null || !t.getKeyword().contains(keyword)) return false;
            }
            return true;
        }).collect(Collectors.toList());

        int total = filtered.size();
        int from = Math.min(skip, total);
        int to = Math.min(skip + limit, total);
        var page = filtered.subList(from, to);

        List<TaskDTO> tasks = page.stream().map(t -> {
            TaskDTO dto = new TaskDTO();
            dto.setId(t.getId());
            dto.setTaskId(t.getId());
            dto.setKeyword(t.getKeyword());
            dto.setSite(t.getSite());
            dto.setStatus(t.getStatus());
            dto.setPostsCollected(t.getPostsCollected());
            dto.setPostCount(t.getPostCount() != null ? t.getPostCount().intValue() : null);
            dto.setCreatedAt(t.getCreatedAt());
            dto.setCompletedAt(t.getEndTime());
            dto.setUpdatedAt(t.getUpdatedAt());
            dto.setErrorMessage(t.getErrorMsg());
            dto.setMinLikes(t.getMinLikes() != null ? t.getMinLikes().intValue() : null);
            dto.setIncludeComments(t.getIncludeComments());
            dto.setIncludeImages(t.getIncludeImages());
            dto.setCommentsPerPost(t.getCommentsPerPost() != null ? t.getCommentsPerPost().intValue() : null);
            dto.setCommentMinLikes(t.getCommentMinLikes() != null ? t.getCommentMinLikes().intValue() : null);
            return dto;
        }).collect(Collectors.toList());

        return ResponseEntity.ok(Map.of("tasks", tasks, "total", total));
    }

    /** GET /api/crawler/tasks/{taskId} */
    @GetMapping("/tasks/{taskId}")
    public ResponseEntity<?> getTask(@PathVariable String taskId) {
        return taskRepository.findById(taskId)
                .map(t -> {
                    TaskDTO dto = new TaskDTO();
                    dto.setId(t.getId());
                    dto.setTaskId(t.getId());
                    dto.setKeyword(t.getKeyword());
                    dto.setSite(t.getSite());
                    dto.setStatus(t.getStatus());
                    dto.setPostsCollected(t.getPostsCollected());
                    dto.setPostCount(t.getPostCount() != null ? t.getPostCount().intValue() : null);
                    dto.setCreatedAt(t.getCreatedAt());
                    dto.setCompletedAt(t.getEndTime());
                    dto.setUpdatedAt(t.getUpdatedAt());
                    dto.setErrorMessage(t.getErrorMsg());
                    dto.setName(t.getKeyword());
                    dto.setSource(t.getSite() != null && t.getSite() == 0 ? "xiaohongshu" : "");
                    return ResponseEntity.ok(dto);
                })
                .orElse(ResponseEntity.notFound().build());
    }

    /** DELETE /api/crawler/tasks/{taskId} */
    @DeleteMapping("/tasks/{taskId}")
    public ResponseEntity<?> deleteTask(@PathVariable String taskId) {
        if (!taskRepository.existsById(taskId))
            return ResponseEntity.notFound().build();
        taskRepository.deleteById(taskId);
        return ResponseEntity.ok(Map.of("message", "task deleted"));
    }

    /** POST /api/crawler/tasks/{taskId}/stop */
    @PostMapping("/tasks/{taskId}/stop")
    public ResponseEntity<?> stopTask(@PathVariable String taskId) {
        return taskRepository.findById(taskId).map(t -> {
            t.setStatus(4); // paused
            taskRepository.save(t);
            return ResponseEntity.ok(Map.of("success", true, "message", "task stopped"));
        }).orElse(ResponseEntity.notFound().build());
    }

    /** GET /api/crawler/status */
    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getStatus() {
        try {
            long taskCount = taskRepository.count();
            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "status", "HEALTHY",
                    "message", "crawler service reachable",
                    "healthy_instances", 1,
                    "taskCount", taskCount
            ));
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of(
                    "success", false,
                    "status", "UNHEALTHY",
                    "message", e.getMessage()
            ));
        }
    }
}
