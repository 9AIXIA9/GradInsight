package com.gradinsight.backend.service;

import com.gradinsight.backend.dto.TaskDTO;
import com.gradinsight.backend.entity.Task;
import com.gradinsight.backend.repository.TaskRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Optional;

@Service
public class TaskService {

    private final TaskRepository repo;
    private final CrawlerDispatchService dispatchService;
    private final com.gradinsight.backend.repository.TaskLogRepository taskLogRepository;

    public TaskService(TaskRepository repo, CrawlerDispatchService dispatchService, com.gradinsight.backend.repository.TaskLogRepository taskLogRepository) {
        this.repo = repo;
        this.dispatchService = dispatchService;
        this.taskLogRepository = taskLogRepository;
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

    public TaskDTO pause(String id) {
        var maybe = repo.findById(id);
        if (maybe.isEmpty()) return null;
        Task t = maybe.get();
        t.setStatus(4); // 4 - paused
        Task saved = repo.save(t);
        writeLog(saved, "paused", saved.getStatus());
        return toDto(saved);
    }

    public TaskDTO resume(String id) {
        var maybe = repo.findById(id);
        if (maybe.isEmpty()) return null;
        Task t = maybe.get();
        t.setStatus(3); // 3 - pending (dispatch)
        Task saved = repo.save(t);
        writeLog(saved, "resumed", saved.getStatus());
        // try dispatch again asynchronously
        try {
            dispatchService.dispatch(saved);
        } catch (Exception ex) {
            saved.setStatus(1);
            saved.setErrorMsg(ex.getMessage());
            saved = repo.save(saved);
            writeLog(saved, "dispatch failed on resume: " + ex.getMessage(), saved.getStatus());
        }
        return toDto(saved);
    }

    public TaskDTO cancel(String id) {
        var maybe = repo.findById(id);
        if (maybe.isEmpty()) return null;
        Task t = maybe.get();
        t.setStatus(5); // 5 - cancelled
        Task saved = repo.save(t);
        writeLog(saved, "cancelled", saved.getStatus());
        return toDto(saved);
    }

    public TaskDTO retry(String id) {
        var maybe = repo.findById(id);
        if (maybe.isEmpty()) return null;
        Task t = maybe.get();
        t.setStatus(3); // pending
        t.setErrorMsg(null);
        Task saved = repo.save(t);
        writeLog(saved, "retry requested", saved.getStatus());
        try {
            dispatchService.dispatch(saved);
        } catch (Exception ex) {
            saved.setStatus(1);
            saved.setErrorMsg(ex.getMessage());
            saved = repo.save(saved);
            writeLog(saved, "dispatch failed on retry: " + ex.getMessage(), saved.getStatus());
        }
        return toDto(saved);
    }

    public List<TaskDTO> list() {
        return repo.findAll().stream().map(this::toDto).collect(Collectors.toList());
    }

    public TaskDTO findById(String id) {
        return repo.findById(id).map(this::toDto).orElse(null);
    }

    public void deleteById(String id) {
        repo.deleteById(id);
    }

    public java.util.List<com.gradinsight.backend.entity.TaskLog> getLogs(String taskId) {
        try {
            return taskLogRepository.findByTaskIdOrderByCreatedAtDesc(taskId);
        } catch (Exception ex) {
            return java.util.Collections.emptyList();
        }
    }

    private TaskDTO toDto(Task t) {
        TaskDTO dto = new TaskDTO();
        dto.setId(t.getId());
        dto.setTaskId(t.getId());          // 兼容字段
        dto.setName(t.getName());
        dto.setSource(t.getSource());
        dto.setKeyword(t.getKeyword());
        dto.setSite(t.getSite());
        dto.setPostCount(t.getPostCount() != null ? t.getPostCount().intValue() : null);
        dto.setIncludeComments(t.getIncludeComments());
        dto.setCommentsPerPost(t.getCommentsPerPost() != null ? t.getCommentsPerPost().intValue() : null);
        dto.setMinLikes(t.getMinLikes() != null ? t.getMinLikes().intValue() : null);
        dto.setCommentMinLikes(t.getCommentMinLikes() != null ? t.getCommentMinLikes().intValue() : null);
        dto.setIncludeImages(t.getIncludeImages());
        dto.setStatus(t.getStatus());       // int, not String
        dto.setCrawlerTaskId(t.getCrawlerTaskId());
        dto.setPostsCollected(t.getPostsCollected());
        dto.setErrorMessage(t.getErrorMsg());
        dto.setCreatedAt(t.getCreatedAt());
        dto.setCompletedAt(t.getEndTime());
        dto.setUpdatedAt(t.getUpdatedAt());
        return dto;
    }

    private Task fromDto(TaskDTO dto) {
        Task t = new Task();
        t.setId(dto.getId());
        t.setName(dto.getName());
        t.setSource(dto.getSource());
        t.setKeyword(dto.getKeyword());
        t.setSite(dto.getSite());
        t.setPostCount(dto.getPostCount() != null ? Long.valueOf(dto.getPostCount()) : null);
        t.setIncludeComments(dto.getIncludeComments());
        t.setCommentsPerPost(dto.getCommentsPerPost() != null ? Long.valueOf(dto.getCommentsPerPost()) : null);
        t.setMinLikes(dto.getMinLikes() != null ? Long.valueOf(dto.getMinLikes()) : null);
        t.setCommentMinLikes(dto.getCommentMinLikes() != null ? Long.valueOf(dto.getCommentMinLikes()) : null);
        t.setIncludeImages(dto.getIncludeImages());
        if (dto.getStatus() != null) t.setStatus(dto.getStatus());
        t.setCrawlerTaskId(dto.getCrawlerTaskId());
        t.setPostsCollected(dto.getPostsCollected());
        t.setErrorMsg(dto.getErrorMessage());
        t.setCreatedAt(dto.getCreatedAt());
        t.setEndTime(dto.getCompletedAt());
        t.setUpdatedAt(dto.getUpdatedAt());
        return t;
    }

    /**
     * 处理爬虫回调，将爬虫任务结果写回 tasks 表（支持通过 crawlerTaskId 或 系统 id 查找）
     */
    public TaskDTO applyCrawlerCallback(String id, String crawlerTaskId, Integer status,
                                        Integer postsCollected, String errorMsg, String endTimeStr) {
        Optional<Task> maybe = Optional.empty();

        if (crawlerTaskId != null && !crawlerTaskId.isBlank()) {
            maybe = repo.findByCrawlerTaskId(crawlerTaskId);
        }

        if ((maybe.isEmpty() || maybe.get() == null) && id != null && !id.isBlank()) {
            maybe = repo.findById(id);
        }

        if (maybe.isEmpty()) return null;

        Task t = maybe.get();

        if (status != null) t.setStatus(status);
        if (postsCollected != null) t.setPostsCollected(postsCollected);
        if (errorMsg != null) t.setErrorMsg(errorMsg);
        if (endTimeStr != null && !endTimeStr.isBlank()) {
            try {
                // 支持 ISO 格式时间戳
                LocalDateTime end = LocalDateTime.parse(endTimeStr, DateTimeFormatter.ISO_DATE_TIME);
                t.setEndTime(end);
            } catch (Exception ex) {
                // ignore parse error
            }
        }

        Task saved = repo.save(t);
        writeLog(saved, "crawler callback: " + (errorMsg == null ? "ok" : errorMsg), status);
        return toDto(saved);
    }

    private void writeLog(Task t, String message, Integer status) {
        try {
            com.gradinsight.backend.entity.TaskLog log = new com.gradinsight.backend.entity.TaskLog();
            log.setTaskId(t.getId());
            log.setMessage(message);
            log.setStatus(status);
            taskLogRepository.save(log);
        } catch (Exception ex) {
            // swallow to avoid breaking main flow
        }
    }
}
