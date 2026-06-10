package com.gradinsight.backend.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
public class TaskDTO {
    private String id;

    @JsonProperty("task_id")
    private String taskId;

    private String name;
    private String source;
    private String keyword;
    private Integer site;

    @JsonProperty("post_count")
    private Integer postCount;

    @JsonProperty("include_comments")
    private Boolean includeComments;

    @JsonProperty("comments_per_post")
    private Integer commentsPerPost;

    @JsonProperty("min_likes")
    private Integer minLikes;

    @JsonProperty("comment_min_likes")
    private Integer commentMinLikes;

    @JsonProperty("include_images")
    private Boolean includeImages;

    private Integer status;

    @JsonProperty("crawler_task_id")
    private String crawlerTaskId;

    @JsonProperty("posts_collected")
    private Integer postsCollected;

    @JsonProperty("error_message")
    private String errorMessage;

    @JsonProperty("created_at")
    private LocalDateTime createdAt;

    @JsonProperty("completed_at")
    private LocalDateTime completedAt;

    @JsonProperty("updated_at")
    private LocalDateTime updatedAt;

    public String getTaskId() {
        return taskId != null ? taskId : id;
    }
}
