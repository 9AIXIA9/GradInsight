package repository

import (
	"context"
	"database/sql"
	"errors"
	"gradinsight-crawler/internal/domain"
	"gradinsight-crawler/internal/model"
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

// ReportProgress 原子累加已爬帖数，返回是否完成
func (r *MysqlRepository) ReportProgress(ctx context.Context, taskID domain.TaskID, crawled uint32) (done bool, err error) {
	return r.taskModel.ReportProgress(ctx, string(taskID), crawled)
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
