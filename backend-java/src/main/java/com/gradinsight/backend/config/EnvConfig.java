package com.gradinsight.backend.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * 纯 Java 的 .env 文件加载器（无外部依赖）。
 *
 * 用法：在 main() 最开头调用 EnvConfig.load()
 *
 * 效果等同于 python-dotenv / godotenv。
 * 将 .env 中的键值对写入 System Properties，
 * Spring Boot 的 ${...} 占位符自动从中读取。
 */
public final class EnvConfig {

    private static final Logger log = LoggerFactory.getLogger(EnvConfig.class);

    private EnvConfig() {}

    /**
     * 加载 .env 文件到 System Properties。
     *
     * 查找顺序：
     *   1. 系统属性 "dotenv.path" 或环境变量 DOTENV_PATH 指定的路径
     *   2. 工作目录下的 .env
     *   3. 找不到则跳过（不报错）
     */
    public static void load() {
        Path envPath = resolvePath();
        log.info("Looking for .env at: {}", envPath.toAbsolutePath());

        if (!Files.exists(envPath)) {
            log.warn(".env NOT FOUND at {}. Using application.properties defaults.",
                    envPath.toAbsolutePath());
            return;
        }

        try {
            int count = 0;
            for (String line : Files.readAllLines(envPath)) {
                String trimmed = line.trim();

                // 跳过空行和注释
                if (trimmed.isEmpty() || trimmed.startsWith("#")) {
                    continue;
                }

                int eq = trimmed.indexOf('=');
                if (eq <= 0) continue; // 无 key 或 key 为空

                String key = trimmed.substring(0, eq).trim();
                String value = trimmed.substring(eq + 1).trim();

                // 去掉可选的双引号或单引号
                if ((value.startsWith("\"") && value.endsWith("\""))
                        || (value.startsWith("'") && value.endsWith("'"))) {
                    value = value.substring(1, value.length() - 1);
                }

                // 只设置尚未被命令行 -D 参数覆盖的值
                if (System.getProperty(key) == null) {
                    System.setProperty(key, value);
                    count++;
                }
            }
            log.info("Loaded {} keys from: {}", count, envPath.toAbsolutePath());
        } catch (IOException e) {
            log.warn("Failed to read .env from {}: {}. Using defaults.",
                    envPath.toAbsolutePath(), e.getMessage());
        }
    }

    private static Path resolvePath() {
        String explicit = System.getProperty("dotenv.path",
                System.getenv("DOTENV_PATH"));
        if (explicit != null && !explicit.isBlank()) {
            return Paths.get(explicit);
        }
        return Paths.get(System.getProperty("user.dir"), ".env");
    }
}
