package com.gradinsight.backend.service;

import com.gradinsight.backend.entity.Task;
import com.gradinsight.backend.repository.TaskRepository;
import com.gradinsight.backend.grpc.CrawlerGrpcClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Service
public class CrawlerDispatchService {
    private static final Logger log = LoggerFactory.getLogger(CrawlerDispatchService.class);

    private final CrawlerGrpcClient crawlerGrpcClient;
    private final TaskRepository taskRepository;

    public CrawlerDispatchService(CrawlerGrpcClient crawlerGrpcClient, TaskRepository taskRepository) {
        this.crawlerGrpcClient = crawlerGrpcClient;
        this.taskRepository = taskRepository;
    }

    @Async("taskExecutor")
    public void dispatch(Task task) {
        int maxRetries = 3;
        int attempt = 0;
        while (attempt < maxRetries) {
            attempt++;
            try {
                log.info("Dispatching task {} attempt {}", task.getId(), attempt);
                crawler.Crawler.CrawlRequest req = crawler.Crawler.CrawlRequest.newBuilder()
                        .setSite(task.getSite() == null ? crawler.Crawler.Site.XIAOHONGSHU : crawler.Crawler.Site.forNumber(task.getSite()))
                        .setKeyword(task.getKeyword() == null ? "" : task.getKeyword())
                        .setPostCount(task.getPostCount() == null ? 100 : task.getPostCount())
                        .setMinLikes(task.getMinLikes() == null ? 0 : task.getMinLikes())
                        .setIncludeComments(task.getIncludeComments() == null ? true : task.getIncludeComments())
                        .setIncludeImages(task.getIncludeImages() == null ? false : task.getIncludeImages())
                        .build();

                crawler.Crawler.CrawlResponse resp = crawlerGrpcClient.startCrawl(req);
                task.setCrawlerTaskId(resp.getTaskId());
                task.setStatus(resp.getSuccess() ? 2 : 1); // 2 - running, 1 - failed
                taskRepository.save(task);
                log.info("Dispatch result for {}: success={}, taskId={}", task.getId(), resp.getSuccess(), resp.getTaskId());
                return;
            } catch (Exception ex) {
                log.warn("Dispatch attempt {} failed for {}: {}", attempt, task.getId(), ex.getMessage());
                if (attempt >= maxRetries) {
                    task.setStatus(1); // failed
                    task.setErrorMsg(ex.getMessage());
                    taskRepository.save(task);
                }
            }
        }
    }
}
