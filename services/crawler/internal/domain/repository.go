package domain

import "context"

// Repository 定义仓库
type Repository interface {
	SaveTask(ctx context.Context, task *Task) error
	SavePostsAndComments(ctx context.Context, taskID TaskID, posts []*Post) error
	SavePosts(ctx context.Context, taskID TaskID, posts []*Post) error
	SaveComments(ctx context.Context, taskID TaskID, postID string, comments []*Comment) error

	// ReportProgress 原子累加已爬帖数，返回任务是否已完成（配额已满）
	ReportProgress(ctx context.Context, taskID TaskID, crawled uint32) (done bool, err error)
}
