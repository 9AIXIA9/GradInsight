package com.gradinsight.backend.dto;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class TaskDTO {
    private Long id;
    private String name;
    private String source;
    private String keywords;
    private String status;
    private LocalDateTime createdAt;
}
