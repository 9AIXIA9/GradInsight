/**
 * GradInsight API 交互模块
 * 用于与后端API进行通信
 */

const API = {
    baseURL: 'http://localhost:8000',
    token: null,
    timeout: 10000, // 添加10秒超时设置
    retryCount: 0,  // 添加重试计数器
    maxRetries: 2,  // 最大重试次数

    // 设置token
    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('token', token);
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            console.log('Token已设置到axios:', token.substring(0, 10) + '...');
        } else {
            localStorage.removeItem('token');
            delete axios.defaults.headers.common['Authorization'];
            console.log('Token已从axios移除');
        }
        // 重置重试计数器
        this.retryCount = 0;
    },

    // 初始化
    init() {
        // 设置axios全局配置
        axios.defaults.baseURL = this.baseURL;
        axios.defaults.timeout = this.timeout;

        // 从localStorage获取token并设置
        const savedToken = localStorage.getItem('token');
        if (savedToken) {
            this.token = savedToken;
            axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
            console.log('初始化时从localStorage恢复token:', savedToken.substring(0, 10) + '...');
        } else {
            // 确保没有token时headers是干净的
            this.token = null;
            delete axios.defaults.headers.common['Authorization'];
        }

        // 添加请求拦截器
        axios.interceptors.request.use(
            (config) => {
                // 每次请求前检查token是否存在且是否已设置到header
                const currentToken = localStorage.getItem('token');
                if (currentToken && !config.headers['Authorization']) {
                    config.headers['Authorization'] = `Bearer ${currentToken}`;
                }
                return config;
            },
            (error) => {
                return Promise.reject(error);
            }
        );

        // 添加响应拦截器
        axios.interceptors.response.use(
            (response) => {
                // 成功响应直接返回
                return response;
            },
            (error) => {
                // 如果是认证错误且不是登录请求，清除token并通知用户
                if (error.response && error.response.status === 401) {
                    // 避免登录API本身的401错误引起无限循环
                    const isAuthRequest = error.config.url.includes('/api/auth/login');

                    if (!isAuthRequest) {
                        // 清除认证状态
                        this.clearAuthState();

                        // 显示通知
                        if (this.retryCount === 0) {
                            console.log('会话已过期，请重新登录');
                            // 可以通过事件触发UI通知
                            const event = new CustomEvent('auth:expired', {
                                detail: { message: '会话已过期，请重新登录' }
                            });
                            window.dispatchEvent(event);
                        }

                        // 防止无限循环重定向
                        if (this.retryCount < this.maxRetries) {
                            this.retryCount++;
                            // 在短暂延迟后重定向到登录页面
                            setTimeout(() => {
                                window.location.href = '/login';
                            }, 500);
                        }
                    }
                }
                return Promise.reject(error);
            }
        );

        // 重置重试计数器
        this.retryCount = 0;
    },

    // 清除所有认证状态
    clearAuthState() {
        localStorage.removeItem('token');
        this.token = null;
        delete axios.defaults.headers.common['Authorization'];

        // 发布认证清除事件，让Vue应用可以响应
        const event = new CustomEvent('auth:cleared');
        window.dispatchEvent(event);
    },

    // 错误处理函数
    handleError(error) {
        console.error('API错误:', error);

        if (error.response) {
            // 服务器返回错误响应
            const status = error.response.status;
            const data = error.response.data;

            // 如果是401错误（未授权）
            if (status === 401) {
                console.log('收到401未授权响应，清除token');
                this.clearAuthState();
                return { message: '登录已过期，请重新登录', status };
            }

            if (data && data.detail) {
                return { message: data.detail, status };
            } else {
                return { message: `请求失败 (${status})`, status };
            }
        } else if (error.request) {
            // 请求已发送但没有收到响应
            return { message: '服务器没有响应，请稍后再试', status: 0 };
        } else {
            // 请求设置出错
            return { message: '请求错误: ' + error.message, status: 0 };
        }
    },

    // 尝试刷新token的方法
    async refreshToken() {
        try {
            // 如果后端提供了刷新token的接口，可以在这里调用
            // 例如: const response = await axios.post('/api/auth/refresh');
            // 如果刷新成功，更新token
            // this.setToken(response.data.access_token);
            // return true;

            // 目前后端没有刷新token的接口，直接返回false
            return false;
        } catch (error) {
            console.error('刷新token失败:', error);
            return false;
        }
    },

    // 用户认证相关API
    auth: {
        // 用户登录
        async login(username, password) {
            try {
                const response = await axios.post('/api/auth/login', { username, password });
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        },

        // 用户注册
        async register(username, password, email) {
            try {
                const response = await axios.post('/api/auth/register', { username, password, email });
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        },

        // 获取当前用户信息
        async getCurrentUser() {
            try {
                const response = await axios.get('/api/auth/me');
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        },

        // 登出
        async logout() {
            try {
                // 如果后端有登出接口
                // await axios.post('/api/auth/logout');

                // 清除本地状态
                API.clearAuthState();
                return { success: true };
            } catch (error) {
                // 即使请求失败，也清除本地状态
                API.clearAuthState();
                return { success: false, error: API.handleError(error) };
            }
        }
    },

    // 高校数据相关API
    posts: {
        // 获取帖子列表
        async getPosts(params = {}) {
            try {
                const response = await axios.get('/api/posts', { params });
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        }
    },

    // 爬虫管理相关API (统一的爬虫管理接口)
    crawler: {
        // 启动爬虫任务（仅限管理员）
        async startCrawl(data) {
            try {
                const response = await axios.post('/api/crawler/start', data);
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        },

        // 获取任务列表（仅限管理员）
        async getTasks(params = {}) {
            try {
                const response = await axios.get('/api/crawler/tasks', { params });
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        },

        // 获取任务详情（仅限管理员）
        async getTaskDetail(taskId) {
            try {
                const response = await axios.get(`/api/crawler/tasks/${taskId}`);
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        },

        // 停止爬虫任务（仅限管理员）
        async stopTask(taskId) {
            try {
                const response = await axios.post(`/api/crawler/tasks/${taskId}/stop`);
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        },

        // 删除爬虫任务（仅限管理员）
        async deleteTask(taskId) {
            try {
                const response = await axios.delete(`/api/crawler/tasks/${taskId}`);
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        },

        // 获取爬虫服务状态（仅限管理员）
        async getStatus() {
            try {
                const response = await axios.get('/api/crawler/status');
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        }
    },

    // 保持向后兼容的任务API (重定向到新的爬虫接口)
    tasks: {
        // 获取任务列表（仅限管理员） - 使用新的爬虫接口
        async getTasks(params = {}) {
            return await API.crawler.getTasks(params);
        },

        // 获取任务详情（仅限管理员） - 使用新的爬虫接口
        async getTaskDetail(taskId) {
            return await API.crawler.getTaskDetail(taskId);
        },

        // 删除任务 - 使用新的爬虫接口
        async deleteTask(taskId) {
            return await API.crawler.deleteTask(taskId);
        },

        // 停止任务 - 使用新的爬虫接口
        async stopTask(taskId) {
            return await API.crawler.stopTask(taskId);
        }
    },

    // 统计数据相关API
    stats: {
        // 获取首页统计数据概览
        async getOverview() {
            try {
                const response = await axios.get('/api/stats/overview');
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        },

        // 获取热门高校榜单
        async getHotSchools(limit = 10) {
            try {
                const response = await axios.get('/api/stats/hot-schools', {
                    params: { limit }
                });
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        },

        // 获取热门专业趋势
        async getTrendingMajors() {
            try {
                const response = await axios.get('/api/stats/trending-majors');
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        },

        // 获取热门城市排行
        async getPopularCities() {
            try {
                const response = await axios.get('/api/stats/popular-cities');
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        },

        // 获取最新动态
        async getLatestNews() {
            try {
                const response = await axios.get('/api/stats/latest-news');
                return { success: true, data: response.data };
            } catch (error) {
                return { success: false, error: API.handleError(error) };
            }
        }
    }
};

// 初始化API模块
API.init();

// 为页面刷新添加事件监听
window.addEventListener('beforeunload', () => {
    // 确保当前token在localStorage中是最新的
    if (API.token) {
        localStorage.setItem('token', API.token);
    }
});

// 监听认证事件
window.addEventListener('auth:cleared', () => {
    console.log('认证已清除，更新UI');
    // Vue应用可以监听此事件进行响应
});

window.addEventListener('auth:expired', (event) => {
    console.log('认证已过期:', event.detail.message);
    // Vue应用可以监听此事件进行响应
});
