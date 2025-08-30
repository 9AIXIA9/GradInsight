/**
 * GradInsight 主应用逻辑
 * 实现路由、状态管理和应用初始化
 */

// 创建Vue应用
const app = Vue.createApp({
    // 设置分隔符，避免与Jinja2冲突
    delimiters: ['${', '}'],

    data() {
        return {
            currentPage: 'home',
            user: null,
            isAdmin: false,
            posts: [],
            tasks: [],
            currentComponent: components.HomePage,
            isInitializing: true,  // 添加初始化状态标志
            authError: null,       // 添加认证错误信息
            loginRedirectTimer: null, // 用于存储重定向定时器
            authCheckInProgress: false // 添加认证检查进行中的标志
        }
    },
    mounted() {
        // 监听认证事件
        this.setupAuthListeners();

        // 先检查用户登录状态，然后初始化路由
        this.initializeApp();

        // 监听浏览器历史变化
        window.addEventListener('popstate', this.handleRouting);

        // 添加刷新页面前的事件处理
        window.addEventListener('beforeunload', this.handleBeforeUnload);
    },
    beforeUnmount() {
        // 组件销毁前清除事件监听和定时器
        window.removeEventListener('popstate', this.handleRouting);
        window.removeEventListener('auth:cleared', this.handleAuthCleared);
        window.removeEventListener('auth:expired', this.handleAuthExpired);
        window.removeEventListener('beforeunload', this.handleBeforeUnload);

        if (this.loginRedirectTimer) {
            clearTimeout(this.loginRedirectTimer);
        }
    },
    methods: {
        // 设置认证事件监听
        setupAuthListeners() {
            // 监听认证清除事件
            window.addEventListener('auth:cleared', this.handleAuthCleared);

            // 监听认证过期事件
            window.addEventListener('auth:expired', this.handleAuthExpired);
        },

        // 处理页面刷新前事件
        handleBeforeUnload() {
            // 确保当前状态同步到localStorage
            if (this.user && this.user.token) {
                localStorage.setItem('token', this.user.token);
                console.log('页面刷新前保存token到localStorage');
            }
        },

        // 处理认证清除事件
        handleAuthCleared() {
            console.log('收到认证清除事件，更新应用状态');
            this.clearUserState();
        },

        // 处理认证过期事件
        handleAuthExpired(event) {
            console.log('收到认证过期事件:', event.detail.message);
            this.authError = event.detail.message;
            this.clearUserState();

            // 如果不是在登录页面，设置定时器重定向到登录页面
            if (window.location.pathname !== '/login') {
                this.loginRedirectTimer = setTimeout(() => {
                    this.navigateTo('/login');
                }, 1000);
            }
        },

        // 清除用户状态
        clearUserState() {
            this.user = null;
            this.isAdmin = false;
        },

        // 初始化应用
        async initializeApp() {
            try {
                this.isInitializing = true;
                console.log('初始化应用...');

                // 先检查用户登录状态
                await this.checkAuthStatus();

                // 然后初始化路由
                this.handleRouting();

            } catch (error) {
                console.error('应用初始化失败:', error);
                // 出错时清除状态
                this.clearAuthState();
            } finally {
                // 无论成功还是失败，都将初始化状态设为false
                this.isInitializing = false;
            }
        },

        // 清除认证状态 (同时调用API的清除方法)
        clearAuthState() {
            API.clearAuthState();
            this.clearUserState();
        },

        // 路由处理
        handleRouting() {
            try {
                // 如果应用还在初始化，等待初始化完成
                if (this.isInitializing) {
                    console.log('应用仍在初始化，延迟路由处理');
                    setTimeout(() => this.handleRouting(), 100);
                    return;
                }

                // 如果正在进行认证检查，也等待完成
                if (this.authCheckInProgress) {
                    console.log('认证检查正在进行中，延迟路由处理');
                    setTimeout(() => this.handleRouting(), 100);
                    return;
                }

                const path = window.location.pathname;
                console.log('当前路径:', path, '用户:', this.user ? this.user.username : '未登录', '是否管理员:', this.isAdmin);

                // 设置当前页面
                if (path === '/' || path === '/index.html') {
                    this.currentPage = 'home';
                    this.currentComponent = components.HomePage;
                } else if (path === '/login') {
                    // 如果已登录，重定向到首页
                    if (this.user) {
                        console.log('已登录用户尝试访问登录页面，重定向到首页');
                        this.navigateTo('/');
                        return;
                    }
                    this.currentPage = 'login';
                    this.currentComponent = components.LoginPage;
                } else if (path === '/register') {
                    // 如果已登录，重定向到首页
                    if (this.user) {
                        console.log('已登录用户尝试访问注册页面，重定向到首页');
                        this.navigateTo('/');
                        return;
                    }
                    this.currentPage = 'register';
                    this.currentComponent = components.RegisterPage;
                } else if (path === '/posts') {
                    this.currentPage = 'posts';
                    this.currentComponent = components.PostsPage;
                } else if (path === '/tasks') {
                    // 检查是否有管理员权限
                    if (!this.user || !this.isAdmin) {
                        console.log('权限不足，重定向到首页');
                        this.navigateTo('/');
                        return;
                    }
                    console.log('进入任务页面');
                    this.currentPage = 'tasks';
                    this.currentComponent = components.TasksPage;
                } else if (path === '/crawler') {
                    // 检查是否有管理员权限
                    if (!this.user || !this.isAdmin) {
                        console.log('权限不足，重定向到首页');
                        this.navigateTo('/');
                        return;
                    }
                    console.log('进入爬虫页面');
                    this.currentPage = 'crawler';
                    this.currentComponent = components.CrawlerPage;
                } else {
                    // 未匹配的路径显示首页
                    this.currentPage = 'home';
                    this.currentComponent = components.HomePage;
                }

                // 在页面切换后初始化下拉菜单
                this.$nextTick(() => {
                    this.initializeDropdowns();
                });
            } catch (error) {
                console.error('路由处理错误:', error);
                // 出错时显示首页
                this.currentPage = 'home';
                this.currentComponent = components.HomePage;
            }
        },

        // 导航到指定页面
        navigateTo(path) {
            // 如果应用还在初始化，等待初始化完成
            if (this.isInitializing) {
                console.log('应用仍在初始化，延迟导航');
                setTimeout(() => this.navigateTo(path), 100);
                return;
            }

            // 如果正在进行认证检查，也等待完成
            if (this.authCheckInProgress) {
                console.log('认证检查正在进行中，延迟导航');
                setTimeout(() => this.navigateTo(path), 100);
                return;
            }

            // 确保路径以 / 开头
            if (!path.startsWith('/')) {
                path = '/' + path;
            }

            // 清除可能存在的重定向定时器
            if (this.loginRedirectTimer) {
                clearTimeout(this.loginRedirectTimer);
                this.loginRedirectTimer = null;
            }

            window.history.pushState({}, '', path);
            this.handleRouting();
        },

        // 初始化下拉菜单
        initializeDropdowns() {
            try {
                const dropdownElementList = document.querySelectorAll('.dropdown-toggle');
                if (dropdownElementList.length > 0) {
                    console.log(`初始化 ${dropdownElementList.length} 个下拉菜单`);
                    dropdownElementList.forEach(dropdownToggleEl => {
                        // 检查是否已经初始化
                        if (!bootstrap.Dropdown.getInstance(dropdownToggleEl)) {
                            new bootstrap.Dropdown(dropdownToggleEl);
                        }
                    });
                }
            } catch (error) {
                console.error('初始化下拉菜单失败:', error);
            }
        },

        // 检查用户登录状态
        async checkAuthStatus() {
            try {
                // 设置认证检查进行中的标志
                this.authCheckInProgress = true;

                const token = localStorage.getItem('token');
                console.log('检查登录状态，token:', token ? (token.substring(0, 10) + '...') : '不存在');

                if (token) {
                    // 设置token到axios
                    API.setToken(token);

                    // 尝试获取用户信息
                    console.log('尝试获取用户信息...');
                    const result = await API.auth.getCurrentUser();
                    console.log('获取用户信息结果:', result.success ? '成功' : '失败');

                    if (result.success) {
                        this.user = result.data;
                        // 确保user对象中也有token，这对于页面刷新前的保存很重要
                        this.user.token = token;
                        this.isAdmin = this.user.role === 'admin';
                        this.authError = null; // 清除之前的认证错误
                        console.log('用户登录状态已更新:', this.user.username, '是否管理员:', this.isAdmin);

                        // 初始化下拉菜单
                        this.$nextTick(() => {
                            this.initializeDropdowns();
                        });
                    } else {
                        // 获取用户信息失败，清除token
                        console.log('获取用户信息失败，清除状态');
                        this.clearAuthState();
                    }
                } else {
                    console.log('没有token，设置为未登录状态');
                    this.clearAuthState();
                }
            } catch (error) {
                console.error('检查登录状态时出错:', error);
                // 出错时也清除状态
                this.clearAuthState();
            } finally {
                // 无论成功还是失败，都将认证检查进行中的标志设为false
                this.authCheckInProgress = false;
            }
        },

        // 处理登录
        handleLogin(user) {
            try {
                console.log('处理登录事件，用户:', user.username);

                // 清除之前的错误信息
                this.authError = null;

                // 更新用户状态
                this.user = user;
                this.isAdmin = user.role === 'admin';

                // 保存token到localStorage
                if (user.token) {
                    console.log('保存token到localStorage和API');
                    API.setToken(user.token);
                } else {
                    console.warn('登录事件中没有收到token');
                }

                this.navigateTo('/');

                // 需要在Vue更新DOM后初始化Bootstrap下拉菜单
                this.$nextTick(() => {
                    this.initializeDropdowns();
                });
            } catch (error) {
                console.error('处理登录事件错误:', error);
                // 出错时清除状态
                this.clearAuthState();
            }
        },

        // 处理注册
        handleRegister(user) {
            // 注册成功后自动重定向到登录页面
            this.navigateTo('/login');
        },

        // 退出登录
        logout() {
            console.log('用户登出');
            // 使用API的logout方法，它内部会调用clearAuthState
            API.auth.logout().then(() => {
                // 无论成功与否，都导航到首页
                this.navigateTo('/');
            });
        },

        // 启动爬虫任务
        startCrawl(data) {
            // 可以在这里处理爬虫任务启动后的逻辑
            console.log('Crawl task started:', data);
        }
    }
});

// 挂载Vue应用
app.mount('#app');

