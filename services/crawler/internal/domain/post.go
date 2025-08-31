package domain

import (
	"time"
)

// Post 帖子模型
type Post struct {
	ID       string    `bson:"_id"`
	TaskID   TaskID    `bson:"task_id"`
	Title    string    `bson:"title"`
	Poster   string    `bson:"poster"`
	Time     time.Time `bson:"time"`
	Location string    `bson:"location"`
	Link     string    `bson:"link"`
	Content  string    `bson:"content"` // 修复：移除"-"标记，允许保存到数据库
	Tags     []string  `bson:"tags"`

	LikeCount    uint64 `bson:"like_count"`
	CommentCount uint64 `bson:"comment_count"`
	CollectCount uint64 `bson:"collect_count"`

	ImageURLs []string   `bson:"image_urls"`
	Comments  []*Comment `bson:"-"`
}

// Comment 评论模型
type Comment struct {
	ID        string    `bson:"_id"`
	TaskID    TaskID    `bson:"task_id"`
	PostID    string    `bson:"post_id"`
	Commenter string    `bson:"commenter"`
	Time      time.Time `bson:"time"`
	Location  string    `bson:"location"`
	Content   string    `bson:"content"`

	LikeCount  uint64 `bson:"like_count"`
	ReplyCount uint64 `bson:"reply_count"`
}
