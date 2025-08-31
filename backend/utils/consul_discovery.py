"""
服务发现模块

提供微服务间的服务发现功能，支持 Consul 等服务注册中心
"""

import consul
import logging
import requests
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class ConsulConfig:
    """Consul配置"""
    host: Optional[str] = None
    port: Optional[int] = None
    timeout: Optional[int] = None

    def __post_init__(self):
        """在初始化后设置默认值"""
        settings = get_settings()
        self.host = self.host or settings.CONSUL_HOST
        self.port = self.port or settings.CONSUL_PORT
        self.timeout = self.timeout or settings.CONSUL_TIMEOUT

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class ConsulServiceDiscovery:
    """基于Consul的服务发现工具"""

    def __init__(self, config: Optional[ConsulConfig] = None):
        self.config = config or ConsulConfig()

    def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """获取服务健康状态

        Args:
            service_name: 服务名称，如 'crawler-service'

        Returns:
            包含服务健康状态的字典
        """
        try:
            # 首先尝试直接检查服务是否在Consul中注册
            catalog_url = f"{self.config.base_url}/v1/catalog/service/{service_name}"
            catalog_response = requests.get(catalog_url, timeout=self.config.timeout)

            if catalog_response.status_code != 200:
                # 如果Consul本身无法访问，返回Consul不可用状态
                return {
                    'success': False,
                    'status': 'CONSUL_UNAVAILABLE',
                    'message': f'无法连接到Consul服务: HTTP {catalog_response.status_code}',
                    'instances': 0,
                    'healthy_instances': 0
                }

            catalog_services = catalog_response.json()

            if not catalog_services:
                # 服务未在Consul中注册，但爬虫服务可能直接运行
                # 尝试直接ping爬虫服务
                return self._check_direct_service_health(service_name)

            # 查询服务健康状态
            health_url = f"{self.config.base_url}/v1/health/service/{service_name}"
            health_response = requests.get(health_url, timeout=self.config.timeout)

            if health_response.status_code == 200:
                services = health_response.json()

                if not services:
                    # 服务在catalog中但health检查失败，可能是健康检查配置问题
                    return self._check_direct_service_health(service_name)

                # 统计健康实例
                healthy_count = 0
                total_count = len(services)

                for service in services:
                    checks = service.get('Checks', [])
                    # 如果没有健康检查或所有检查都通过，认为是健康的
                    if not checks or all(check.get('Status') == 'passing' for check in checks):
                        healthy_count += 1

                # 判断整体状态
                if healthy_count == 0:
                    # 所有实例都不健康，尝试直接检查服务
                    return self._check_direct_service_health(service_name)
                elif healthy_count == total_count:
                    return {
                        'success': True,
                        'status': 'HEALTHY',
                        'message': f'服务 {service_name} 运行正常 ({healthy_count}/{total_count} 实例健康)',
                        'instances': total_count,
                        'healthy_instances': healthy_count,
                        'services': services
                    }
                else:
                    return {
                        'success': True,
                        'status': 'PARTIAL',
                        'message': f'服务 {service_name} 部分实例健康 ({healthy_count}/{total_count})',
                        'instances': total_count,
                        'healthy_instances': healthy_count,
                        'services': services
                    }
            else:
                return self._check_direct_service_health(service_name)

        except requests.exceptions.RequestException as e:
            logger.error(f"Consul连接失败: {str(e)}")
            # Consul连接失败时，尝试直接检查爬虫服务
            return self._check_direct_service_health(service_name)
        except Exception as e:
            logger.error(f"获取服务健康状态失败: {str(e)}")
            return self._check_direct_service_health(service_name)

    def _check_direct_service_health(self, service_name: str) -> Dict[str, Any]:
        """直接检查爬虫服务的健康状态（当Consul不可用时的fallback）

        Args:
            service_name: 服务名称

        Returns:
            包含服务健康状态的字典
        """
        try:
            # 这里需要根据你的爬虫服务实际情况调���
            # 假设爬虫服务运行在localhost:8999
            import socket
            from core.config import get_settings

            settings = get_settings()
            host = settings.CRAWLER_HOST
            port = settings.CRAWLER_PORT

            # 尝试连接爬虫服务端口
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)  # 3秒超时
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                return {
                    'success': True,
                    'status': 'HEALTHY',
                    'message': f'爬虫服务直接连接成功 ({host}:{port})',
                    'instances': 1,
                    'healthy_instances': 1,
                    'check_method': 'direct_tcp'
                }
            else:
                return {
                    'success': False,
                    'status': 'UNHEALTHY',
                    'message': f'爬虫服务连接失败 ({host}:{port})，请检查服务是否启动',
                    'instances': 0,
                    'healthy_instances': 0,
                    'check_method': 'direct_tcp'
                }

        except Exception as e:
            logger.error(f"直接检查服务健康状态失败: {str(e)}")
            return {
                'success': False,
                'status': 'ERROR',
                'message': f'无法检查服务状态: {str(e)}',
                'instances': 0,
                'healthy_instances': 0,
                'check_method': 'direct_tcp'
            }

    def list_services(self) -> Dict[str, Any]:
        """列出所有注册的服务

        Returns:
            包含所有服务列表的字典
        """
        try:
            url = f"{self.config.base_url}/v1/catalog/services"
            response = requests.get(url, timeout=self.config.timeout)

            if response.status_code == 200:
                services = response.json()
                return {
                    'success': True,
                    'services': services,
                    'count': len(services)
                }
            else:
                return {
                    'success': False,
                    'message': f'获取服务列表失败: HTTP {response.status_code}',
                    'services': {},
                    'count': 0
                }

        except Exception as e:
            logger.error(f"获取服务列表失败: {str(e)}")
            return {
                'success': False,
                'message': f'获取服务列表失败: {str(e)}',
                'services': {},
                'count': 0
            }

    def get_service_instances(self, service_name: str) -> List[Dict[str, Any]]:
        """获取服务实例详情

        Args:
            service_name: 服务名称

        Returns:
            服务实例列表
        """
        try:
            url = f"{self.config.base_url}/v1/catalog/service/{service_name}"
            response = requests.get(url, timeout=self.config.timeout)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取服务实例失败: HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"获取服务实例失败: {str(e)}")
            return []
