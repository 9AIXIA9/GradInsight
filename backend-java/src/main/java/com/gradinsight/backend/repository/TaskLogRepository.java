package com.gradinsight.backend.repository;

import com.gradinsight.backend.entity.TaskLog;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface TaskLogRepository extends JpaRepository<TaskLog, Long> {
    List<TaskLog> findByTaskIdOrderByCreatedAtDesc(String taskId);
}

