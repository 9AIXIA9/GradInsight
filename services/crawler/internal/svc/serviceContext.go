package svc

import (
	"context"
	"time"

	"github.com/zeromicro/go-zero/core/bloom"
	"github.com/zeromicro/go-zero/core/logx"
	"github.com/zeromicro/go-zero/core/stores/sqlx"
	"gradinsight-crawler/internal/config"
	"gradinsight-crawler/internal/domain"
	"gradinsight-crawler/internal/infra/ctrl"
	"gradinsight-crawler/internal/infra/redisx"
	"gradinsight-crawler/internal/infra/repository"
	"gradinsight-crawler/internal/infra/resource"
	"gradinsight-crawler/internal/model"
)

type ServiceContext struct {
	Config    *config.Config
	TaskQueue domain.TaskQueue
	Repo      domain.Repository
}

func MustNewServiceContext(c *config.Config) *ServiceContext {
	mysqlClient := sqlx.NewMysql(c.MySQL.DSN)
	redisClient := redisx.MustNewClient(c.Redisx)

	taskModel := model.NewTasksModel(mysqlClient, c.CacheRedis)
	postsModel := model.NewPostsModel(mysqlClient, c.CacheRedis)
	commentsModel := model.NewCommentsModel(mysqlClient, c.CacheRedis)

	repo := repository.NewMysqlRepository(taskModel, postsModel, commentsModel)
	filter := bloom.New(redisClient, c.BloomFilter.Key, c.BloomFilter.Bits)
	resourcePool := resource.MustNewResourcePool(c.Resource)
	taskQueue := ctrl.NewTaskQueue(&c.TaskQueue, repo, filter, resourcePool)

	// 启动时恢复未完成的任务（状态为 Running 或 Pending）
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := taskQueue.Resume(ctx); err != nil {
		logx.Errorf("恢复未完成任务失败: %v", err)
	}

	return &ServiceContext{
		Config:    c,
		TaskQueue: taskQueue,
		Repo:      repo,
	}
}
