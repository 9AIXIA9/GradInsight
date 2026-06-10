package model

import (
	"database/sql"
	"encoding/json"
	"gradinsight-crawler/internal/domain"
	"time"
)

// TaskFromDomain 将领域模型转换为数据库模型
func TaskFromDomain(task *domain.Task) *Tasks {
	if task == nil {
		return nil
	}

	// 处理错误消息
	var errMsg sql.NullString
	if task.Err != nil {
		errMsg = sql.NullString{
			String: task.Err.Error(),
			Valid:  true,
		}
	}

	// 处理结束时间
	var endTime sql.NullTime
	if !task.EndTime.IsZero() {
		endTime = sql.NullTime{
			Time:  task.EndTime,
			Valid: true,
		}
	}

	return &Tasks{
		Id:              string(task.ID),
		ParentId:        sql.NullString{},
		WaitSubCount:    0,
		Status:          int64(task.Status),
		PostsCollected:  uint64(task.PostsCollected),
		StartTime:       task.StartTime,
		EndTime:         endTime,
		ErrorMsg:        errMsg,
		Site:            int64(task.Site),
		Keyword:         task.Keyword,
		PostCount:       task.PostCount,
		MinLikes:        task.MinLikes,
		CommentMinLikes: task.CommentMinLikes,
		CommentsPerPost: task.CommentsPerPost,
		IncludeComments: boolToInt64(task.IncludeComments),
		IncludeImages:   boolToInt64(task.IncludeImages),
	}
}

// PostFromDomain 将Post领域模型转换为数据库模型
func PostFromDomain(post *domain.Post) *Posts {
	if post == nil {
		return nil
	}

	// 处理位置
	var location sql.NullString
	if post.Location != "" {
		location = sql.NullString{
			String: post.Location,
			Valid:  true,
		}
	}

	// 处理标签
	var tags sql.NullString
	if len(post.Tags) > 0 {
		tagsJSON, _ := json.Marshal(post.Tags)
		tags = sql.NullString{
			String: string(tagsJSON),
			Valid:  true,
		}
	}

	// 处理图片URL
	var imageUrls sql.NullString
	if len(post.ImageURLs) > 0 {
		imageUrlsJSON, _ := json.Marshal(post.ImageURLs)
		imageUrls = sql.NullString{
			String: string(imageUrlsJSON),
			Valid:  true,
		}
	}

	return &Posts{
		Id:           post.ID,
		TaskId:       string(post.TaskID),
		Title:        post.Title,
		Content:      post.Content, // 添加Content字段映射
		Poster:       post.Poster,
		PostTime:     post.Time,
		Location:     location,
		Link:         post.Link,
		Tags:         tags,
		LikeCount:    post.LikeCount,
		CommentCount: post.CommentCount,
		CollectCount: post.CollectCount,
		ImageUrls:    imageUrls,
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}
}

// CommentFromDomain 将Comment领域模型转换为数据库模型
func CommentFromDomain(comment *domain.Comment) *Comments {
	if comment == nil {
		return nil
	}

	// 处理位置
	var location sql.NullString
	if comment.Location != "" {
		location = sql.NullString{
			String: comment.Location,
			Valid:  true,
		}
	}

	return &Comments{
		Id:          comment.ID,
		TaskId:      string(comment.TaskID),
		PostId:      comment.PostID,
		Commenter:   comment.Commenter,
		CommentTime: comment.Time,
		Location:    location,
		Content:     comment.Content,
		LikeCount:   comment.LikeCount,
		ReplyCount:  comment.ReplyCount,
		CreatedAt:   time.Now(),
	}
}

// boolToInt64 将bool转换为int64
func boolToInt64(b bool) int64 {
	if b {
		return 1
	}
	return 0
}

// TagsFromJSON 从JSON字符串解析标签数组
func TagsFromJSON(tagsJSON sql.NullString) []string {
	if !tagsJSON.Valid {
		return nil
	}

	var tags []string
	err := json.Unmarshal([]byte(tagsJSON.String), &tags)
	if err != nil {
		return nil
	}
	return tags
}

// ImageURLsFromJSON 从JSON字符串解析图片URL数组
func ImageURLsFromJSON(urlsJSON sql.NullString) []string {
	if !urlsJSON.Valid {
		return nil
	}

	var urls []string
	err := json.Unmarshal([]byte(urlsJSON.String), &urls)
	if err != nil {
		return nil
	}
	return urls
}
