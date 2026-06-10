package domain

import "context"

// TaskQueue 任务队列
type TaskQueue interface {
	Dispatcher()                      // 任务调度器
	AddTask(task *Task) error         // 添加新任务
	ProcessTask(task *Task)           // 处理任务
	Resume(ctx context.Context) error // 恢复未完成任务
	Stop(ctx context.Context)
}
