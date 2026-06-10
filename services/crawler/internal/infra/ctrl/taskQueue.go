package ctrl

import (
	"context"
	"errors"
	"fmt"
	"gradinsight-crawler/internal/config"
	"gradinsight-crawler/internal/domain"
	"gradinsight-crawler/internal/infra/crawler"
	"gradinsight-crawler/internal/infra/site"
	"sync"
	"time"

	"github.com/zeromicro/go-zero/core/logx"
	"github.com/zeromicro/go-zero/core/threading"
)

type TaskQueue struct {
	repo         domain.Repository
	filter       domain.Filter
	resourcePool domain.ResourcePool
	crawler      domain.Crawler

	batchSize uint64 // 每批次认领帖数

	mutex      sync.RWMutex
	taskChan   chan *domain.Task
	workerPool chan struct{}
	stopChan   chan struct{}
	waitGroup  sync.WaitGroup
	isRunning  bool
}

func NewTaskQueue(conf *config.TaskQueue, repo domain.Repository, filter domain.Filter, resourcePool domain.ResourcePool) domain.TaskQueue {
	if repo == nil {
		logx.Severef("仓库不能为空")
	}
	tq := &TaskQueue{
		repo:         repo,
		filter:       filter,
		resourcePool: resourcePool,
		crawler:      crawler.NewCrawler(),
		batchSize:    conf.BatchSize,
		mutex:        sync.RWMutex{},
		taskChan:     make(chan *domain.Task, conf.MaxTaskCacheSize),
		workerPool:   make(chan struct{}, conf.MaxWorkers),
		stopChan:     make(chan struct{}),
		waitGroup:    sync.WaitGroup{},
		isRunning:    true,
	}
	if tq.batchSize == 0 {
		tq.batchSize = 3
	}
	threading.GoSafe(tq.Dispatcher)
	return tq
}

// ---- 生命周期 ----

func (tq *TaskQueue) AddTask(task *domain.Task) error {
	defer tq.persistTask(task)
	logx.Infof("收到任务：%v", task.ID)
	task.StartTime = time.Now()
	task.Status = domain.StatusPending

	// 一次性入队多份，让多个 worker 并发抢同一任务
	workers := cap(tq.workerPool)
	for i := 0; i < workers; i++ {
		if err := tq.sendTaskToQueue(task); err != nil {
			return err
		}
	}
	return nil
}

func (tq *TaskQueue) Stop(ctx context.Context) {
	tq.mutex.Lock()
	if !tq.isRunning {
		tq.mutex.Unlock()
		return
	}
	tq.isRunning = false
	close(tq.stopChan)
	tq.mutex.Unlock()
	tq.waitGroup.Wait()
	tq.resourcePool.Close(ctx)
}

// ---- 调度 ----

func (tq *TaskQueue) Dispatcher() {
	for {
		select {
		case task := <-tq.taskChan:
			tq.workerPool <- struct{}{}
			tq.waitGroup.Add(1)
			threading.GoSafe(func() {
				defer func() { <-tq.workerPool; tq.waitGroup.Done() }()
				task.Status = domain.StatusRunning
				tq.ProcessTask(task)
			})
		case <-tq.stopChan:
			return
		}
	}
}

func (tq *TaskQueue) sendTaskToQueue(task *domain.Task) error {
	tq.mutex.Lock()
	defer tq.mutex.Unlock()
	if !tq.isRunning {
		task.Status = domain.StatusFailed
		task.Err = errors.New("任务队列未运行")
		return task.Err
	}
	tq.taskChan <- task
	return nil
}

// ---- 核心：批次认领循环（先爬后报）----

func (tq *TaskQueue) ProcessTask(task *domain.Task) {
	defer func() { tq.finalizeTask(task) }()

	// 1. 获取爬虫资源
	s, err := tq.prepareSite(task)
	if err != nil {
		task.Err = err
		return
	}

	resource, err := tq.acquireResource(task)
	if err != nil {
		task.Err = err
		return
	}
	if resource == nil || task.Status == domain.StatusPending {
		return
	}

	// 2. 爬取链接（最多 batchSize 篇）
	links, err := tq.crawler.CollectPostLinks(resource.Browser(), tq.filter, s, task.Keyword, tq.batchSize, task.MinLikes)
	if err != nil {
		tq.resourcePool.Put(resource)
		task.Err = fmt.Errorf("收集链接失败: %w", err)
		return
	}

	// 3. 爬取详情（本地计数，避免并发写 task.PostsCollected）
	posts, batchCrawled := tq.collectPosts(resource, s, links, task)
	tq.resourcePool.Put(resource)

	// 4. 保存 + 原子报进度
	tq.saveCrawlResults(task, posts)
	done, err := tq.repo.ReportProgress(context.Background(), task.ID, batchCrawled)
	if err != nil {
		task.Err = fmt.Errorf("报进度失败: %w", err)
		return
	}

	logx.Infof("任务 %v 本批+%d 篇（目标 %d）", task.ID, batchCrawled, task.PostCount)

	if done {
		task.Status = domain.StatusCompleted
		return
	}

	// 配额未满，重新入队让其他 worker 来抢
	task.Status = domain.StatusPending
	if err := tq.sendTaskToQueue(task); err != nil {
		task.Err = err
	}
}

// ---- 辅助方法 ----

func (tq *TaskQueue) persistTask(task *domain.Task) {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	if err := tq.repo.SaveTask(ctx, task); err != nil {
		logx.Errorf("保存任务失败：%v", err)
	}
}

func (tq *TaskQueue) prepareSite(task *domain.Task) (domain.Site, error) {
	s, err := site.Convert(task.Site)
	if err != nil {
		return nil, fmt.Errorf("转换站点错误: %w", err)
	}
	return s, nil
}

func (tq *TaskQueue) acquireResource(task *domain.Task) (domain.ResourceUnit, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	resource, err := tq.resourcePool.Get(ctx)
	if err != nil {
		if errors.Is(err, context.DeadlineExceeded) {
			task.Status = domain.StatusPending
			if err = tq.AddTask(task); err != nil {
				return nil, fmt.Errorf("获取资源失败且无法重新加入队列：%w", task.Err)
			}
			return nil, nil
		}
		return nil, fmt.Errorf("无法获取资源实例: %w", err)
	}
	return resource, nil
}

func (tq *TaskQueue) collectPosts(resource domain.ResourceUnit, s domain.Site, links []string, task *domain.Task) ([]*domain.Post, uint32) {
	posts := make([]*domain.Post, 0, len(links))
	crawled := uint32(0)
	for i, link := range links {
		logx.Debugf("爬取 %d/%d: %s", i+1, len(links), link)
		post, err := tq.crawler.CollectPostDetail(resource.Browser(), s, link, &domain.CollectPostDetailOption{
			IncludeComments: task.IncludeComments, IncludeImages: task.IncludeImages,
			CommentsPerPost: task.CommentsPerPost, MinLikes: task.MinLikes,
		})
		if err != nil {
			logx.Errorf("爬取帖子 %v 出错: %v", link, err)
			continue
		}
		posts = append(posts, post)
		crawled++
		logx.Infof("成功爬取: %s", post.Title)
	}
	return posts, crawled
}

func (tq *TaskQueue) saveCrawlResults(task *domain.Task, posts []*domain.Post) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := tq.repo.SavePostsAndComments(ctx, task.ID, posts); err != nil {
		logx.Errorf("保存帖子失败: %v", err)
	}
}

func (tq *TaskQueue) finalizeTask(task *domain.Task) {
	if task.Status == domain.StatusPending {
		return
	}
	task.EndTime = time.Now()
	if task.Err != nil {
		task.Status = domain.StatusFailed
	}
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	if err := tq.repo.SaveTask(ctx, task); err != nil {
		logx.Errorf("保存任务失败: %v", err)
	}
}
