package com.gradinsight.backend.controller;

import com.gradinsight.backend.dto.TaskDTO;
import com.gradinsight.backend.service.TaskService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    @PostMapping
    public ResponseEntity<TaskDTO> createTask(@RequestBody TaskDTO task) {
        TaskDTO saved = taskService.save(task);
        return ResponseEntity.ok(saved);
    }

    @GetMapping
    public ResponseEntity<List<TaskDTO>> listTasks() {
        return ResponseEntity.ok(taskService.list());
    }

    @GetMapping("/{id}")
    public ResponseEntity<TaskDTO> getTask(@PathVariable String id) {
        TaskDTO t = taskService.findById(id);
        if (t == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(t);
    }

    @GetMapping("/{id}/status")
    public ResponseEntity<?> getTaskStatus(@PathVariable String id) {
        TaskDTO t = taskService.findById(id);
        if (t == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(java.util.Map.of(
                "id", t.getId(),
                "status", t.getStatus(),
                "crawlerTaskId", t.getCrawlerTaskId()
        ));
    }

    @PatchMapping("/{id}/pause")
    public ResponseEntity<TaskDTO> pauseTask(@PathVariable String id) {
        TaskDTO t = taskService.pause(id);
        if (t == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(t);
    }

    @PatchMapping("/{id}/resume")
    public ResponseEntity<TaskDTO> resumeTask(@PathVariable String id) {
        TaskDTO t = taskService.resume(id);
        if (t == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(t);
    }

    @PatchMapping("/{id}/cancel")
    public ResponseEntity<TaskDTO> cancelTask(@PathVariable String id) {
        TaskDTO t = taskService.cancel(id);
        if (t == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(t);
    }

    @PostMapping("/{id}/retry")
    public ResponseEntity<TaskDTO> retryTask(@PathVariable String id) {
        TaskDTO t = taskService.retry(id);
        if (t == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(t);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteTask(@PathVariable String id) {
        // simple delete
        TaskDTO t = taskService.findById(id);
        if (t == null) return ResponseEntity.notFound().build();
        taskService.deleteById(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/{id}/logs")
    public ResponseEntity<?> getTaskLogs(@PathVariable String id) {
        var logs = taskService.getLogs(id);
        return ResponseEntity.ok(logs);
    }
}
