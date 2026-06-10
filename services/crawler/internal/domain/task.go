package domain

import (
	"gradinsight-crawler/proto"
	"time"
)

type TaskID string

// Task — 统一任务模型，无父子概念
type Task struct {
	ID             TaskID     `bson:"_id"`
	Status         TaskStatus `bson:"status"`
	PostsCollected uint32     `bson:"posts_collected"`
	StartTime      time.Time  `bson:"start_time"`
	EndTime        time.Time  `bson:"end_time"`
	Err            error      `bson:"err,omitempty"`

	Site            proto.Site `bson:"site"`
	Keyword         string     `bson:"keyword"`
	PostCount       uint64     `bson:"post_count"`
	MinLikes        uint64     `bson:"min_likes"`
	CommentMinLikes uint64     `bson:"comment_min_likes"`
	CommentsPerPost uint64     `bson:"comments_per_post"`
	IncludeComments bool       `bson:"include_comments"`
	IncludeImages   bool       `bson:"include_images"`
}

type TaskStatus int

const (
	StatusCompleted TaskStatus = iota
	StatusFailed
	StatusRunning
	StatusPending
)

func (s TaskStatus) String() string {
	switch s {
	case StatusCompleted:
		return "已完成"
	case StatusFailed:
		return "失败"
	case StatusRunning:
		return "运行中"
	case StatusPending:
		return "等待中"
	default:
		return "未知状态"
	}
}
