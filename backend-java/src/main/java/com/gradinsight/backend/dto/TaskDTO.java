package com.gradinsight.backend.dto;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class TaskDTO {
    private String id;
    private String name;
    private String source;
    private String keyword;
    private String status;
    private String crawlerTaskId;
    private LocalDateTime createdAt;
}
