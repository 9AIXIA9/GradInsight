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
    private String id; // 对应 SQL 脚本中的 VARCHAR(64) 主键

    @Column(name = "parent_id", length = 64)
    private String parentId;

    @Column(name = "wait_sub_count")
    private Long waitSubCount = 0L;

    /**
     * status: 与脚本保持一致为 int
     */
    private Integer status = 3; // 默认待处理

    @Column(name = "posts_collected")
    private Integer postsCollected = 0;

    @Column(name = "start_time")
    private LocalDateTime startTime;

    @Column(name = "end_time")
    private LocalDateTime endTime;

    @Column(name = "error_msg", columnDefinition = "TEXT")
    private String errorMsg;

    @Column(name = "name")
    private String name;

    @Column(name = "source")
    private String source;

    private Integer site;

    /** keyword 对应脚本的 keyword */
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
        if (this.id == null) this.id = UUID.randomUUID().toString();
    }

    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
