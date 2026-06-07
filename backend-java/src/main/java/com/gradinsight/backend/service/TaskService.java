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
    private final com.gradinsight.backend.grpc.CrawlerGrpcClient crawlerGrpcClient;

    public TaskService(TaskRepository repo, com.gradinsight.backend.grpc.CrawlerGrpcClient crawlerGrpcClient) {
        this.repo = repo;
        this.crawlerGrpcClient = crawlerGrpcClient;
    }

    public TaskDTO save(TaskDTO dto) {
        Task t = fromDto(dto);
        Task saved = repo.save(t);
        TaskDTO out = toDto(saved);

        // 发起 gRPC 调用下发爬虫任务（异步/同步可根据需要调整）
        try {
            crawler.CrawlRequest req = crawler.CrawlRequest.newBuilder()
                    .setSite(crawler.Site.XIAOHONGSHU)
                    .setKeyword(saved.getKeywords() == null ? "" : saved.getKeywords())
                    .setPostCount(100)
                    .setMinLikes(0)
                    .setIncludeComments(true)
                    .setIncludeImages(false)
                    .build();

            crawler.CrawlResponse resp = crawlerGrpcClient.startCrawl(req);
            out.setStatus(resp.getSuccess() ? "DISPATCHED" : "FAILED_DISPATCH");
            // 可把 resp.getTaskId() 保存到任务表扩展字段中，或另建表记录
        } catch (Exception ex) {
            out.setStatus("ERROR_DISPATCH");
        }

        return out;
    }

    public List<TaskDTO> list() {
        return repo.findAll().stream().map(this::toDto).collect(Collectors.toList());
    }

    public TaskDTO findById(Long id) {
        return repo.findById(id).map(this::toDto).orElse(null);
    }

    private TaskDTO toDto(Task t) {
        TaskDTO dto = new TaskDTO();
        dto.setId(t.getId());
        dto.setName(t.getName());
        dto.setSource(t.getSource());
        dto.setKeywords(t.getKeywords());
        dto.setStatus(t.getStatus());
        dto.setCreatedAt(t.getCreatedAt());
        return dto;
    }

    private Task fromDto(TaskDTO dto) {
        Task t = new Task();
        t.setId(dto.getId());
        t.setName(dto.getName());
        t.setSource(dto.getSource());
        t.setKeywords(dto.getKeywords());
        t.setStatus(dto.getStatus());
        t.setCreatedAt(dto.getCreatedAt());
        return t;
    }
}
