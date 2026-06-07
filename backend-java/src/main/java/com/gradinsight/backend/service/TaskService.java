package com.gradinsight.backend.service;

import com.gradinsight.backend.dto.TaskDTO;
import com.gradinsight.backend.entity.Task;
import com.gradinsight.backend.repository.TaskRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class TaskService {

    private final TaskRepository repo;
    private final CrawlerDispatchService dispatchService;

    public TaskService(TaskRepository repo, CrawlerDispatchService dispatchService) {
        this.repo = repo;
        this.dispatchService = dispatchService;
    }

    public TaskDTO save(TaskDTO dto) {
        Task t = fromDto(dto);
        Task saved = repo.save(t);
        TaskDTO out = toDto(saved);

        // 异步下发：把任务状态置为 3 (待处理) 或特定值表示正在派发
        saved.setStatus(3); // 3 - pending / dispatching
        saved = repo.save(saved);
        out = toDto(saved);

        // 提交后台派发，不阻塞请求
        try {
            dispatchService.dispatch(saved);
        } catch (Exception ex) {
            // 如果提交异步失败，标记为错误
            saved.setStatus(1);
            saved.setErrorMsg(ex.getMessage());
            saved = repo.save(saved);
            out = toDto(saved);
        }

        return out;
    }

    public List<TaskDTO> list() {
        return repo.findAll().stream().map(this::toDto).collect(Collectors.toList());
    }

    public TaskDTO findById(String id) {
        return repo.findById(id).map(this::toDto).orElse(null);
    }

    private TaskDTO toDto(Task t) {
        TaskDTO dto = new TaskDTO();
        dto.setId(t.getId());
        dto.setName(t.getName());
        dto.setSource(t.getSource());
        dto.setKeyword(t.getKeyword());
        dto.setStatus(t.getStatus() == null ? null : String.valueOf(t.getStatus()));
        dto.setCrawlerTaskId(t.getCrawlerTaskId());
        dto.setCreatedAt(t.getCreatedAt());
        return dto;
    }

    private Task fromDto(TaskDTO dto) {
        Task t = new Task();
        t.setId(dto.getId());
        t.setName(dto.getName());
        t.setSource(dto.getSource());
        t.setKeyword(dto.getKeyword());
        if (dto.getStatus() != null) {
            try {
                t.setStatus(Integer.parseInt(dto.getStatus()));
            } catch (NumberFormatException ignored) {
            }
        }
        t.setCrawlerTaskId(dto.getCrawlerTaskId());
        t.setCreatedAt(dto.getCreatedAt());
        return t;
    }
}
