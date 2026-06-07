package com.gradinsight.backend.controller;

import com.gradinsight.backend.dto.TaskDTO;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    @PostMapping
    public ResponseEntity<?> createTask(@RequestBody TaskDTO task) {
        // TODO: 保存任务并调用爬虫服务
        return ResponseEntity.ok("created");
    }

    @GetMapping
    public ResponseEntity<List<TaskDTO>> listTasks() {
        // TODO: 查询任务列表
        return ResponseEntity.ok(List.of());
    }

    @GetMapping("/{id}")
    public ResponseEntity<TaskDTO> getTask(@PathVariable Long id) {
        // TODO: 返回任务详情
        return ResponseEntity.ok(new TaskDTO());
    }
}
