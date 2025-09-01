package svc

import (
	"github.com/zeromicro/go-zero/core/bloom"
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
	//创建Mysql客户端
	mysqlClient := sqlx.NewMysql(c.MySQL.DSN)

	//创建Redis客户端
	redisClient := redisx.MustNewClient(c.Redisx)

	//初始化仓库
	taskModel := model.NewTasksModel(mysqlClient, c.CacheRedis)
	postsModel := model.NewPostsModel(mysqlClient, c.CacheRedis)
	commentsModel := model.NewCommentsModel(mysqlClient, c.CacheRedis)

	repo := repository.NewMysqlRepository(taskModel, postsModel, commentsModel)

	// 初始化布隆过滤器
	filter := bloom.New(redisClient, c.BloomFilter.Key, c.BloomFilter.Bits) //并发安全

	//初始化资源池
	resourcePool := resource.MustNewResourcePool(c.Resource)

	// 使用配置的工作线程数初始化任务队列
	taskQueue := ctrl.NewTaskQueue(&c.TaskQueue, repo, filter, resourcePool)

	return &ServiceContext{
		Config:    c,
		TaskQueue: taskQueue,
		Repo:      repo,
	}
}
