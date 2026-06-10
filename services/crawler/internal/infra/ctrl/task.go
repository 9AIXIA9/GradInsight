package ctrl

import (
	"gradinsight-crawler/internal/domain"
	"gradinsight-crawler/internal/infra/utils/snowflake"
	"gradinsight-crawler/proto"
	"time"
)

// NewTask 创建新任务
func NewTask(request *proto.CrawlRequest) *domain.Task {
	return &domain.Task{
		ID:              snowflake.GenerateID(),
		Status:          domain.StatusPending,
		PostsCollected:  0,
		Err:             nil,
		StartTime:       time.Time{},
		EndTime:         time.Time{},
		Site:            request.Site,
		Keyword:         request.Keyword,
		PostCount:       request.PostCount,
		MinLikes:        request.MinLikes,
		CommentMinLikes: request.CommentMinLikes,
		CommentsPerPost: request.CommentsPerPost,
		IncludeComments: request.IncludeComments,
		IncludeImages:   request.IncludeImages,
	}
}
