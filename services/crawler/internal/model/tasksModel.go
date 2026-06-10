package model

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/zeromicro/go-zero/core/stores/cache"
	"github.com/zeromicro/go-zero/core/stores/sqlx"
)

var _ TasksModel = (*customTasksModel)(nil)

type (
	TasksModel interface {
		tasksModel
		// ReportProgress 原子累加已爬帖数，返回 (是否配额已满)
		ReportProgress(ctx context.Context, taskID string, crawled uint32) (done bool, err error)
	}

	customTasksModel struct {
		*defaultTasksModel
	}
)

// ReportProgress 原子累加 + 检查完成
func (m *customTasksModel) ReportProgress(ctx context.Context, taskID string, crawled uint32) (bool, error) {
	key := fmt.Sprintf("%s%v", cacheGradinsightTasksIdPrefix, taskID)

	_, err := m.ExecCtx(ctx, func(ctx context.Context, conn sqlx.SqlConn) (sql.Result, error) {
		query := `UPDATE tasks SET
			posts_collected = posts_collected + ?,
			status = CASE WHEN posts_collected + ? >= post_count THEN 0 ELSE 2 END,
			end_time = CASE WHEN posts_collected + ? >= post_count THEN NOW() ELSE end_time END
		WHERE id = ? AND posts_collected < post_count`
		return conn.ExecCtx(ctx, query, crawled, crawled, crawled, taskID)
	}, key)
	if err != nil {
		return false, err
	}

	// 读取是否完成
	var full bool
	_ = m.QueryRowCtx(ctx, &full, key, func(ctx context.Context, conn sqlx.SqlConn, v any) error {
		return conn.QueryRowCtx(ctx, v, "SELECT CAST(posts_collected >= post_count AS SIGNED) FROM tasks WHERE id = ?", taskID)
	})

	return full, nil
}

func NewTasksModel(conn sqlx.SqlConn, c cache.CacheConf, opts ...cache.Option) TasksModel {
	return &customTasksModel{
		defaultTasksModel: newTasksModel(conn, c, opts...),
	}
}
