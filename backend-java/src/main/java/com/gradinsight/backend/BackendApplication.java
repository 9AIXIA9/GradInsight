package com.gradinsight.backend;

import com.gradinsight.backend.config.EnvConfig;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class BackendApplication {
    public static void main(String[] args) {
        // 在 Spring Boot 启动前加载 .env → System Properties
        // 优先级: -D 参数 > 系统环境变量 > .env > application.properties 默认值
        EnvConfig.load();
        SpringApplication.run(BackendApplication.class, args);
    }
}
