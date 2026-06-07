# backend-java (SpringBoot3 skeleton)

这是为大作业准备的 SpringBoot3 后端骨架示例，目标是将原有 `backend`（FastAPI）替换为 Java 主后端。

快速运行：

1. 进入目录并构建：

```bash
cd backend-java
mvn package
```

2. 运行：

```bash
mvn spring-boot:run
```

配置：编辑 `src/main/resources/application.properties` 填写 MySQL/Redis/分析服务地址等。

说明：当前代码为骨架，包含基础控制器和 DTO。下一步建议：

- 集成数据库实体与 Repository
- 实现认证（Spring Security 或 Sa-Token）
- 调用 Go 爬虫（gRPC 或 REST）和 Python 分析服务
- 将现有 FastAPI 业务逐步迁移到该项目
