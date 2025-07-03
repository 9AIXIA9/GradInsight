package repository

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"gradinsight-crawler/internal/domain"
	"gradinsight-crawler/internal/model"
	"time"
)

// MysqlRepository MySQL仓库实现
type MysqlRepository struct {
	taskModel    model.TasksModel
	postModel    model.PostsModel
	commentModel model.CommentsModel
}

// NewMysqlRepository 创建MySQL仓库实例
func NewMysqlRepository(taskModel model.TasksModel, postModel model.PostsModel, commentModel model.CommentsModel) domain.Repository {
	return &MysqlRepository{
		taskModel:    taskModel,
		postModel:    postModel,
		commentModel: commentModel,
	}
}

// SaveTask 保存任务，如果ID已存在则更新，不存在则插入
func (r *MysqlRepository) SaveTask(ctx context.Context, task *domain.Task) error {
	if task == nil {
		return errors.New("任务为空")
	}
	
	// 将领域模型转换为数据库模型
	dbTask := model.TaskFromDomain(task)
	if dbTask == nil {
		return errors.New("转换任务模型失败")
	}
	
	// 先查询是否存在
	_, err := r.taskModel.FindOne(ctx, string(task.ID))
	if err == nil {
		// 已存在，执行更新
		return r.taskModel.Update(ctx, dbTask)
	} else if errors.Is(err, sql.ErrNoRows) {
		// 不存在，执行插入
		_, err := r.taskModel.Insert(ctx, dbTask)
		return err
	}
	
	// 其他错误
	return err
}

// UpdateParentTask 更新父任务状态
func (r *MysqlRepository) UpdateParentTask(ctx context.Context, task *domain.Task) error {
	// 检查任务有效性
	if task == nil {
		return errors.New("任务为空")
	}
	
	// 检查任务是否有父任务
	if task.ParentID == "" {
		return errors.New("该任务没有父任务")
	}
	
	// 查询父任务
	parentTask, err := r.taskModel.FindOne(ctx, string(task.ParentID))
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return fmt.Errorf("未找到父任务: %s", task.ParentID)
		}
		return err
	}
	
	// 更新父任务：减少等待子任务数并增加帖子收集数
	parentTask.WaitSubCount -= 1
	parentTask.PostsCollected += uint64(task.PostsCollected)
	
	// 如果等待子任务数归零，则将任务标记为完成状态
	if parentTask.WaitSubCount == 0 {
		parentTask.Status = int64(domain.StatusCompleted)
		parentTask.EndTime = sql.NullTime{
			Time:  time.Now(),
			Valid: true,
		}
	}
	
	// 更新父任务
	return r.taskModel.Update(ctx, parentTask)
}

// SavePosts 保存爬取到的帖子
func (r *MysqlRepository) SavePosts(ctx context.Context, taskID domain.TaskID, posts []*domain.Post) error {
	if len(posts) == 0 {
		return nil
	}
	
	// 处理每个帖子
	for _, post := range posts {
		post.TaskID = taskID
		
		// 检查帖子是否已存在
		_, err := r.postModel.FindOne(ctx, post.ID)
		if err == nil {
			// 帖子已存在，跳过
			continue
		} else if !errors.Is(err, sql.ErrNoRows) {
			// 其他错误
			return err
		}
		
		// 帖子不存在，插入
		dbPost := model.PostFromDomain(post)
		_, err = r.postModel.Insert(ctx, dbPost)
		if err != nil {
			return err
		}
	}
	
	return nil
}

// SavePostsAndComments 保存爬取到的帖子和评论
func (r *MysqlRepository) SavePostsAndComments(ctx context.Context, taskID domain.TaskID, posts []*domain.Post) error {
	if len(posts) == 0 {
		return nil
	}
	
	// 先保存所有帖子
	if err := r.SavePosts(ctx, taskID, posts); err != nil {
		return err
	}
	
	// 保存所有评论
	for _, post := range posts {
		if len(post.Comments) > 0 {
			if err := r.SaveComments(ctx, taskID, post.ID, post.Comments); err != nil {
				return err
			}
		}
	}
	
	return nil
}

// SaveComments 保存爬取到的评论
func (r *MysqlRepository) SaveComments(ctx context.Context, taskID domain.TaskID, postID string, comments []*domain.Comment) error {
	if len(comments) == 0 {
		return nil
	}
	
	// 处理每个评论
	for _, comment := range comments {
		comment.TaskID = taskID
		comment.PostID = postID
		
		// 检查评论是否已存在
		_, err := r.commentModel.FindOne(ctx, comment.ID)
		if err == nil {
			// 评论已存在，跳过
			continue
		} else if !errors.Is(err, sql.ErrNoRows) {
			// 其他错误
			return err
		}
		
		// 评论不存在，插入
		dbComment := model.CommentFromDomain(comment)
		_, err = r.commentModel.Insert(ctx, dbComment)
		if err != nil {
			return err
		}
	}
	
	return nil
}
