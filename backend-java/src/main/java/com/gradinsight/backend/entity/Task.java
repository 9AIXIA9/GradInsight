package com.gradinsight.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@Entity
@Table(name = "tasks")
public class Task {
    @Id
    @Column(length = 64)
    private String id;

    @Column(name = "parent_id", length = 64)
    private String parentId;

    @Column(name = "wait_sub_count")
    private Long waitSubCount = 0L;

    /** 0-完成 1-失败 2-运行中 3-待处理 4-分治 */
    private Integer status = 3;

    @Column(name = "posts_collected")
    private Integer postsCollected = 0;

    @Column(name = "start_time")
    private LocalDateTime startTime;

    @Column(name = "end_time")
    private LocalDateTime endTime;

    @Column(name = "error_msg", columnDefinition = "TEXT")
    private String errorMsg;

    /** 站点: 0-小红书 */
    @Column(name = "site")
    private Integer site;

    @Column(name = "keyword")
    private String keyword;

    @Column(name = "post_count")
    private Long postCount;

    @Column(name = "min_likes")
    private Long minLikes;

    @Column(name = "comment_min_likes")
    private Long commentMinLikes;

    @Column(name = "comments_per_post")
    private Long commentsPerPost;

    @Column(name = "include_comments")
    private Boolean includeComments = false;

    @Column(name = "include_images")
    private Boolean includeImages = false;

    @Column(name = "crawler_task_id", length = 64)
    private String crawlerTaskId;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    public void prePersist() {
        if (this.createdAt == null) this.createdAt = LocalDateTime.now();
        if (this.startTime == null) this.startTime = LocalDateTime.now();
        if (this.id == null) this.id = UUID.randomUUID().toString();
    }

    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
