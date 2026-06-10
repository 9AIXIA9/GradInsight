package domain

import "context"

// TaskQueue 任务队列
type TaskQueue interface {
	Dispatcher()              // 任务调度器
	AddTask(task *Task) error // 添加新任务
	ProcessTask(task *Task)   // 处理任务（批次认领循环）
	Stop(ctx context.Context)
}
