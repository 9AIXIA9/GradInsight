import logging
import time
from typing import Dict, Any

import grpc

from app.grpc_client.crawler_client import CrawlerClient, CrawlerServiceConfig

logger = logging.getLogger(__name__)


class CrawlerService:
    def __init__(self, config: Dict[str, Any]):
        self.client_config = CrawlerServiceConfig(
            host=config["host"],
            port=config["port"],
            timeout=config["timeout"],
            max_retries=config["max_retries"]
        )
        self.client = None  # 单例模式
        # 初始化时就创建连接
        self._get_client()

    def _get_client(self):
        """获取或创建客户端连接"""
        if self.client is None:
            self.client = CrawlerClient(self.client_config)
            self.client.connect()
        return self.client

    async def start_crawl(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """启动爬虫任务"""
        max_attempts = 2  # 连接级别重试
        for attempt in range(max_attempts):
            try:
                client = self._get_client()
                return client.start_crawl(**request_data)
            except grpc.RpcError as e:
                logger.error(f"gRPC调用错误 (尝试 {attempt + 1}/{max_attempts}): {str(e)}")
                # 连接错误时重置连接
                if self.client:
                    try:
                        self.client.close()
                    except:
                        pass
                    self.client = None

                if attempt < max_attempts - 1:
                    time.sleep(1)  # 等待1秒后重试
            except Exception as e:
                logger.error(f"爬虫服务调用失败: {str(e)}")
                raise

        raise Exception("爬虫服务调用失败，超过最大重试次数")

    async def stop_crawl(self, task_id: str) -> Dict[str, Any]:
        """停止爬虫任务"""
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                client = self._get_client()
                result = client.stop_crawl(task_id)
                return result
            except grpc.RpcError as e:
                logger.error(f"停止爬虫任务gRPC调用错误 (尝试 {attempt + 1}/{max_attempts}): {str(e)}")
                if self.client:
                    try:
                        self.client.close()
                    except:
                        pass
                    self.client = None

                if attempt < max_attempts - 1:
                    time.sleep(1)
            except Exception as e:
                logger.error(f"停止爬虫任务失败: {str(e)}")
                raise

        raise Exception("停止爬虫任务失败，超过最大重试次数")

    async def get_status(self) -> Dict[str, Any]:
        """获取爬虫服务状态"""
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                client = self._get_client()
                status = client.get_status()
                return status
            except grpc.RpcError as e:
                logger.error(f"获取服务状态gRPC调用错误 (尝试 {attempt + 1}/{max_attempts}): {str(e)}")
                if self.client:
                    try:
                        self.client.close()
                    except:
                        pass
                    self.client = None

                if attempt < max_attempts - 1:
                    time.sleep(1)
            except Exception as e:
                logger.error(f"获取任务状态失败: {str(e)}")
                raise

        raise Exception("获取服务状态失败，超过最大重试次数")

    def close(self):
        """关闭服务连接"""
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                logger.error(f"关闭爬虫服务连接失败: {str(e)}")
            finally:
                self.client = None
