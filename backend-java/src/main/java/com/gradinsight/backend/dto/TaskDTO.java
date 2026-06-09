package com.gradinsight.backend.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
public class TaskDTO {
    private String id;
    private String taskId;        // 兼容字段 = id
    private String name;
    private String source;
    private String keyword;
    private Integer site;
    private Integer postCount;
    private Boolean includeComments;
    private Integer commentsPerPost;
    private Integer minLikes;
    private Integer commentMinLikes;
    private Boolean includeImages;
    private Integer status;       // int: 0完成 1失败 2运行中 3已停止 4等待中
    private String crawlerTaskId;
    private Integer postsCollected;
    private String errorMessage;  // 对应 error_msg
    private LocalDateTime createdAt;
    private LocalDateTime completedAt;  // 对应 end_time
    private LocalDateTime updatedAt;

    // 兼容 getter：前端访问 task_id 时返回 id
    public String getTaskId() {
        return taskId != null ? taskId : id;
    }
}
