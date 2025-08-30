/**
 * GradInsight 前端组件定义
 * 包含各个页面和功能组件
 */

// 首页组件
const HomePage = {
    template: `
        <div>
            <!-- 英雄区域 -->
            <div class="hero-section text-center py-5 mb-5" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <div class="container">
                    <h1 class="display-3 fw-bold mb-4">GradInsight</h1>
                    <p class="display-6 mb-3">高校数据分析平台</p>
                    <p class="lead fs-5 mb-4">基于小红书等社交平台的高校信息智能分析系统</p>
                    <p class="fs-6 mb-4">发现高校数据背后的洞察，助力学生择校与教育决策</p>
                    
                    <div v-if="!user" class="mt-4">
                        <a @click.prevent="$parent.navigateTo('/register')" class="btn btn-light btn-lg me-3 px-4 py-2" style="cursor: pointer;">
                            <i class="bi bi-person-plus me-2"></i>立即注册
                        </a>
                        <a @click.prevent="$parent.navigateTo('/login')" class="btn btn-outline-light btn-lg px-4 py-2" style="cursor: pointer;">
                            <i class="bi bi-box-arrow-in-right me-2"></i>登录系统
                        </a>
                    </div>
                    <div v-else class="mt-4">
                        <a @click.prevent="$parent.navigateTo('/posts')" class="btn btn-light btn-lg me-3 px-4 py-2" style="cursor: pointer;">
                            <i class="bi bi-search me-2"></i>浏览高校数据
                        </a>
                        <a v-if="isAdmin" @click.prevent="$parent.navigateTo('/crawler')" class="btn btn-outline-light btn-lg px-4 py-2" style="cursor: pointer;">
                            <i class="bi bi-gear me-2"></i>启动爬虫任务
                        </a>
                    </div>
                </div>
            </div>

            <!-- 数据统计 -->
            <div class="container mb-5">
                <div class="row text-center">
                    <div class="col-md-3 mb-4">
                        <div class="card border-0 shadow-sm h-100">
                            <div class="card-body">
                                <div class="text-primary mb-3">
                                    <i class="bi bi-database-fill" style="font-size: 2.5rem;"></i>
                                </div>
                                <h3 class="fw-bold text-primary">{{ stats.totalPosts || '10K+' }}</h3>
                                <p class="text-muted mb-0">高校相关帖子</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-4">
                        <div class="card border-0 shadow-sm h-100">
                            <div class="card-body">
                                <div class="text-success mb-3">
                                    <i class="bi bi-chat-dots-fill" style="font-size: 2.5rem;"></i>
                                </div>
                                <h3 class="fw-bold text-success">{{ stats.totalComments || '50K+' }}</h3>
                                <p class="text-muted mb-0">用户评论数据</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-4">
                        <div class="card border-0 shadow-sm h-100">
                            <div class="card-body">
                                <div class="text-warning mb-3">
                                    <i class="bi bi-building" style="font-size: 2.5rem;"></i>
                                </div>
                                <h3 class="fw-bold text-warning">{{ stats.totalSchools || '500+' }}</h3>
                                <p class="text-muted mb-0">覆盖高校数量</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-4">
                        <div class="card border-0 shadow-sm h-100">
                            <div class="card-body">
                                <div class="text-info mb-3">
                                    <i class="bi bi-graph-up" style="font-size: 2.5rem;"></i>
                                </div>
                                <h3 class="fw-bold text-info">{{ stats.totalTasks || '100+' }}</h3>
                                <p class="text-muted mb-0">完成爬虫任务</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 热门高校榜单 -->
            <div class="container mb-5">
                <h2 class="text-center mb-5">
                    <i class="bi bi-fire text-danger me-2"></i>热门高校榜单
                    <small class="text-muted fs-6 d-block mt-2">基于最近7天社交媒体讨论热度</small>
                </h2>
                <div class="row">
                    <div class="col-md-8 mx-auto">
                        <div class="card border-0 shadow-sm">
                            <div class="card-body p-0">
                                <div v-for="(school, index) in hotSchools" :key="index" 
                                     class="d-flex align-items-center p-3 border-bottom">
                                    <div class="rank-badge me-3">
                                        <span class="badge fs-6 fw-bold" 
                                              :class="index < 3 ? 'bg-gradient bg-warning text-dark' : 'bg-secondary'">
                                            {{ index + 1 }}
                                        </span>
                                    </div>
                                    <div class="flex-grow-1">
                                        <h6 class="mb-1 fw-bold">{{ school.name }}</h6>
                                        <small class="text-muted">{{ school.location }} · {{ school.type }}</small>
                                    </div>
                                    <div class="text-end">
                                        <div class="text-primary fw-bold">{{ school.posts }}</div>
                                        <small class="text-muted">相关帖子</small>
                                    </div>
                                    <div class="ms-3">
                                        <span class="badge bg-light text-dark">
                                            <i class="bi bi-arrow-up text-success me-1"></i>{{ school.trend }}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 最新动态 -->
            <div class="bg-light py-5 mb-5">
                <div class="container">
                    <h2 class="text-center mb-5">
                        <i class="bi bi-newspaper text-info me-2"></i>最新动态
                    </h2>
                    <div class="row">
                        <div class="col-md-6 mb-4" v-for="news in latestNews" :key="news.id">
                            <div class="card border-0 shadow-sm h-100">
                                <div class="card-body">
                                    <div class="d-flex align-items-start mb-3">
                                        <div class="text-primary me-3">
                                            <i :class="news.icon" style="font-size: 1.5rem;"></i>
                                        </div>
                                        <div class="flex-grow-1">
                                            <h6 class="fw-bold mb-2">{{ news.title }}</h6>
                                            <p class="text-muted small mb-2">{{ news.content }}</p>
                                            <div class="d-flex justify-content-between align-items-center">
                                                <small class="text-muted">
                                                    <i class="bi bi-clock me-1"></i>{{ news.time }}
                                                </small>
                                                <span class="badge" :class="'bg-' + news.type">{{ news.category }}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 核心功能 -->
            <div class="container mb-5">
                <h2 class="text-center mb-5">核心功能</h2>
                <div class="row">
                    <div class="col-md-4 mb-4">
                        <div class="card feature-card h-100 border-0 shadow-sm">
                            <div class="card-body text-center p-4">
                                <div class="text-primary mb-3">
                                    <i class="bi bi-cloud-download" style="font-size: 3rem;"></i>
                                </div>
                                <h5 class="card-title fw-bold">智能数据采集</h5>
                                <p class="card-text text-muted">
                                    基于先进的爬虫技术，从小红书等社交平台自动采集高校相关数据，
                                    包括用户讨论、评价、热点话题等，为分析提供丰富的数据源。
                                </p>
                                <div class="mt-3">
                                    <span class="badge bg-primary me-2">小红书</span>
                                    <span class="badge bg-secondary me-2">自动化</span>
                                    <span class="badge bg-success">实时采集</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-4">
                        <div class="card feature-card h-100 border-0 shadow-sm">
                            <div class="card-body text-center p-4">
                                <div class="text-success mb-3">
                                    <i class="bi bi-cpu" style="font-size: 3rem;"></i>
                                </div>
                                <h5 class="card-title fw-bold">深度数据分析</h5>
                                <p class="card-text text-muted">
                                    运用大数据分析技术，对采集的高校数据进行多维度分析，
                                    挖掘用户关注热点、情感倾向、话题趋势等有价值的洞察信息。
                                </p>
                                <div class="mt-3">
                                    <span class="badge bg-success me-2">情感分析</span>
                                    <span class="badge bg-info me-2">趋势预测</span>
                                    <span class="badge bg-warning">热点挖掘</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-4">
                        <div class="card feature-card h-100 border-0 shadow-sm">
                            <div class="card-body text-center p-4">
                                <div class="text-info mb-3">
                                    <i class="bi bi-bar-chart" style="font-size: 3rem;"></i>
                                </div>
                                <h5 class="card-title fw-bold">可视化展示</h5>
                                <p class="card-text text-muted">
                                    通过直观的图表、报告和仪表板，清晰展示分析结果，
                                    帮助用户快速理解数据洞察，为择校和教育决策提供有力支持。
                                </p>
                                <div class="mt-3">
                                    <span class="badge bg-info me-2">图表展示</span>
                                    <span class="badge bg-danger me-2">报告生成</span>
                                    <span class="badge bg-dark">决策支持</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 技术架构展示 -->
            <div class="container mb-5">
                <h2 class="text-center mb-5">
                    <i class="bi bi-layers text-primary me-2"></i>技术架构
                </h2>
                <div class="row">
                    <div class="col-md-10 mx-auto">
                        <div class="card border-0 shadow-sm">
                            <div class="card-body p-4">
                                <div class="row text-center">
                                    <div class="col-md-3 mb-4">
                                        <div class="tech-item p-3 rounded bg-light">
                                            <i class="bi bi-globe text-primary" style="font-size: 2rem;"></i>
                                            <h6 class="mt-2 fw-bold">前端技术</h6>
                                            <small class="text-muted">Vue.js + Bootstrap</small>
                                        </div>
                                    </div>
                                    <div class="col-md-3 mb-4">
                                        <div class="tech-item p-3 rounded bg-light">
                                            <i class="bi bi-server text-success" style="font-size: 2rem;"></i>
                                            <h6 class="mt-2 fw-bold">后端服务</h6>
                                            <small class="text-muted">Python FastAPI</small>
                                        </div>
                                    </div>
                                    <div class="col-md-3 mb-4">
                                        <div class="tech-item p-3 rounded bg-light">
                                            <i class="bi bi-spider text-warning" style="font-size: 2rem;"></i>
                                            <h6 class="mt-2 fw-bold">爬虫引擎</h6>
                                            <small class="text-muted">Go + gRPC</small>
                                        </div>
                                    </div>
                                    <div class="col-md-3 mb-4">
                                        <div class="tech-item p-3 rounded bg-light">
                                            <i class="bi bi-database text-info" style="font-size: 2rem;"></i>
                                            <h6 class="mt-2 fw-bold">数据存储</h6>
                                            <small class="text-muted">MySQL + Redis</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 用户评价 -->
            <div class="bg-light py-5 mb-5">
                <div class="container">
                    <h2 class="text-center mb-5">
                        <i class="bi bi-chat-heart text-danger me-2"></i>用户评价
                    </h2>
                    <div class="row">
                        <div class="col-md-4 mb-4" v-for="review in userReviews" :key="review.id">
                            <div class="card border-0 shadow-sm h-100">
                                <div class="card-body p-4">
                                    <div class="d-flex align-items-center mb-3">
                                        <div class="avatar-circle bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" 
                                             style="width: 50px; height: 50px;">
                                            {{ review.name.charAt(0) }}
                                        </div>
                                        <div>
                                            <h6 class="mb-1 fw-bold">{{ review.name }}</h6>
                                            <small class="text-muted">{{ review.role }}</small>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <span v-for="i in 5" :key="i" 
                                              :class="i <= review.rating ? 'text-warning' : 'text-muted'">
                                            <i class="bi bi-star-fill"></i>
                                        </span>
                                    </div>
                                    <p class="text-muted mb-0">"{{ review.comment }}"</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 数据洞察预览 -->
            <div class="container mb-5">
                <h2 class="text-center mb-5">
                    <i class="bi bi-lightbulb text-warning me-2"></i>数据洞察预览
                </h2>
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <div class="card border-0 shadow-sm h-100">
                            <div class="card-header bg-primary text-white">
                                <h6 class="mb-0">
                                    <i class="bi bi-trending-up me-2"></i>热门专业趋势
                                </h6>
                            </div>
                            <div class="card-body">
                                <div v-for="major in trendingMajors" :key="major.name" class="d-flex justify-content-between align-items-center mb-3">
                                    <div>
                                        <span class="fw-bold">{{ major.name }}</span>
                                        <small class="text-muted d-block">{{ major.category }}</small>
                                    </div>
                                    <div class="text-end">
                                        <span class="badge bg-success">+{{ major.growth }}%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 mb-4">
                        <div class="card border-0 shadow-sm h-100">
                            <div class="card-header bg-info text-white">
                                <h6 class="mb-0">
                                    <i class="bi bi-geo-alt me-2"></i>热门城市排行
                                </h6>
                            </div>
                            <div class="card-body">
                                <div v-for="city in popularCities" :key="city.name" class="d-flex justify-content-between align-items-center mb-3">
                                    <div>
                                        <span class="fw-bold">{{ city.name }}</span>
                                        <small class="text-muted d-block">{{ city.region }}</small>
                                    </div>
                                    <div class="text-end">
                                        <span class="text-primary fw-bold">{{ city.schools }}</span>
                                        <small class="text-muted d-block">所高校</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 使用场景 -->
            <div class="bg-light py-5 mb-5">
                <div class="container">
                    <h2 class="text-center mb-5">适用场景</h2>
                    <div class="row">
                        <div class="col-md-6 mb-4">
                            <div class="d-flex">
                                <div class="text-primary me-3">
                                    <i class="bi bi-mortarboard" style="font-size: 2rem;"></i>
                                </div>
                                <div>
                                    <h5 class="fw-bold">学生择校指导</h5>
                                    <p class="text-muted mb-0">
                                        帮助高中生及家长了解不同高校的真实情况，包括校园生活、
                                        专业特色、就业前景等，为择校提供数据支撑。
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-4">
                            <div class="d-flex">
                                <div class="text-success me-3">
                                    <i class="bi bi-building" style="font-size: 2rem;"></i>
                                </div>
                                <div>
                                    <h5 class="fw-bold">高校品牌管理</h5>
                                    <p class="text-muted mb-0">
                                        协助高校了解自身在社交媒体上的形象和声誉，
                                        监控舆情动态，优化品牌传播策略。
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-4">
                            <div class="d-flex">
                                <div class="text-info me-3">
                                    <i class="bi bi-graph-up-arrow" style="font-size: 2rem;"></i>
                                </div>
                                <div>
                                    <h5 class="fw-bold">教育趋势研究</h5>
                                    <p class="text-muted mb-0">
                                        为教育研究机构提供社交媒体数据分析，
                                        洞察教育热点话题和发展趋势。
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-4">
                            <div class="d-flex">
                                <div class="text-warning me-3">
                                    <i class="bi bi-people" style="font-size: 2rem;"></i>
                                </div>
                                <div>
                                    <h5 class="fw-bold">招生营销优化</h5>
                                    <p class="text-muted mb-0">
                                        帮助高校招生办了解目标学生群体的关注点，
                                        优化招生宣传内容和渠道策略。
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 平台优势 -->
            <div class="container mb-5">
                <h2 class="text-center mb-5">平台优势</h2>
                <div class="row align-items-center">
                    <div class="col-md-6 mb-4">
                        <div class="pe-md-4">
                            <h3 class="fw-bold mb-3">
                                <i class="bi bi-shield-check text-success me-2"></i>
                                安全可靠
                            </h3>
                            <p class="text-muted mb-4">
                                采用严格的数据安全和隐私保护措施，确保用户数据和分析结果的安全性。
                                所有数据传输和存储都经过加密处理。
                            </p>
                            
                            <h3 class="fw-bold mb-3">
                                <i class="bi bi-lightning text-warning me-2"></i>
                                高效便捷
                            </h3>
                            <p class="text-muted">
                                自动化的数据采集和分析流程，大大提高工作效率。
                                用户只需简单配置，即可获得全面的分析报告。
                            </p>
                        </div>
                    </div>
                    <div class="col-md-6 mb-4">
                        <div class="ps-md-4">
                            <h3 class="fw-bold mb-3">
                                <i class="bi bi-gear text-primary me-2"></i>
                                智能分析
                            </h3>
                            <p class="text-muted mb-4">
                                基于先进的机器学习和自然语言处理技术，
                                提供深度的数据洞察和智能化的分析结果。
                            </p>
                            
                            <h3 class="fw-bold mb-3">
                                <i class="bi bi-graph-up text-info me-2"></i>
                                实时更新
                            </h3>
                            <p class="text-muted">
                                支持实时数据更新和动态分析，确保用户获得最新、
                                最准确的高校信息和趋势洞察。
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 开始使用 -->
            <div class="bg-primary text-white py-5">
                <div class="container text-center">
                    <h2 class="fw-bold mb-3">准备开始探索高校数据了吗？</h2>
                    <p class="lead mb-4">立即注册，开启您的数据分析之旅</p>
                    
                    <div v-if="!user">
                        <a @click.prevent="$parent.navigateTo('/register')" class="btn btn-light btn-lg me-3 px-4 py-2">
                            <i class="bi bi-person-plus me-2"></i>免费注册
                        </a>
                        <a @click.prevent="$parent.navigateTo('/login')" class="btn btn-outline-light btn-lg px-4 py-2">
                            <i class="bi bi-box-arrow-in-right me-2"></i>已有账号
                        </a>
                    </div>
                    <div v-else>
                        <div class="mb-3">
                            <h4>欢迎回来，{{ user.username }}！</h4>
                            <p class="mb-4">您的角色：{{ user.role === 'admin' ? '管理员' : '普通用户' }}</p>
                        </div>
                        <a @click.prevent="$parent.navigateTo('/posts')" class="btn btn-light btn-lg me-3 px-4 py-2" style="cursor: pointer;">
                            <i class="bi bi-search me-2"></i>浏览数据
                        </a>
                        <a v-if="isAdmin" @click.prevent="$parent.navigateTo('/crawler')" class="btn btn-outline-light btn-lg me-3 px-4 py-2" style="cursor: pointer;">
                            <i class="bi bi-gear me-2"></i>管理爬虫
                        </a>
                        <a v-if="isAdmin" @click.prevent="$parent.navigateTo('/tasks')" class="btn btn-outline-light btn-lg px-4 py-2" style="cursor: pointer;">
                            <i class="bi bi-list-task me-2"></i>查看任务
                        </a>
                    </div>
                </div>
            </div>

            <!-- 页脚信息 -->
            <div class="bg-light py-4 mt-5">
                <div class="container">
                    <div class="row">
                        <div class="col-md-6">
                            <h5 class="fw-bold">GradInsight</h5>
                            <p class="text-muted small">
                                专业的高校数据分析平台，基于社交媒体数据为教育决策提供支持。
                            </p>
                        </div>
                        <div class="col-md-6 text-md-end">
                            <p class="text-muted small mb-1">
                                <i class="bi bi-envelope me-1"></i>
                                技术支持：gradinsight@support.com
                            </p>
                            <p class="text-muted small">
                                <i class="bi bi-shield-check me-1"></i>
                                数据安全 · 隐私保护 · 合规采集
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    props: ['user'],
    data() {
        return {
            stats: {
                totalPosts: null,
                totalComments: null,
                totalSchools: null,
                totalTasks: null
            },
            hotSchools: [],
            latestNews: [],
            userReviews: [
                {
                    id: 1,
                    name: '张同学',
                    role: '高三学生',
                    rating: 5,
                    comment: '通过GradInsight了解到很多高校的真实情况，对我的志愿填报帮助很大！数据分析很专业，界面也很友好。'
                },
                {
                    id: 2,
                    name: '李老师',
                    role: '高校招生办',
                    rating: 5,
                    comment: '这个平台让我们能够及时了解学生和家长对学校的真实看法，对改进招生策略很有价值。'
                },
                {
                    id: 3,
                    name: '王研究员',
                    role: '教育研究者',
                    rating: 4,
                    comment: '数据维度丰富，分析深入，为教育趋势研究提供了重要的数据支撑。期待更多功能！'
                }
            ],
            trendingMajors: [],
            popularCities: [],
            loading: true
        }
    },
    computed: {
        isAdmin() {
            return this.user && this.user.role === 'admin';
        }
    },
    async mounted() {
        await this.loadStats();
    },
    methods: {
        async loadStats() {
            this.loading = true;
            try {
                // 并行加载所有数据
                const promises = [
                    API.stats.getOverview(),
                    API.stats.getHotSchools(5),
                    API.stats.getTrendingMajors(),
                    API.stats.getPopularCities(),
                    API.stats.getLatestNews()
                ];

                const [
                    statsResult,
                    hotSchoolsResult,
                    majorsResult,
                    citiesResult,
                    newsResult
                ] = await Promise.all(promises);

                // 更新统计数据
                if (statsResult.success) {
                    this.stats = statsResult.data;
                } else {
                    console.error('Failed to load stats:', statsResult.error);
                    // 使用默认值
                    this.stats = {
                        totalPosts: '暂无数据',
                        totalComments: '暂无数据',
                        totalSchools: '暂无数据',
                        totalTasks: '暂无数据'
                    };
                }

                // 更新热门高校数据
                if (hotSchoolsResult.success) {
                    this.hotSchools = hotSchoolsResult.data;
                } else {
                    console.error('Failed to load hot schools:', hotSchoolsResult.error);
                }

                // 更新热门专业数据
                if (majorsResult.success) {
                    this.trendingMajors = majorsResult.data;
                } else {
                    console.error('Failed to load trending majors:', majorsResult.error);
                }

                // 更新热门城市数据
                if (citiesResult.success) {
                    this.popularCities = citiesResult.data;
                } else {
                    console.error('Failed to load popular cities:', citiesResult.error);
                }

                // 更新最新动态
                if (newsResult.success) {
                    this.latestNews = newsResult.data;
                } else {
                    console.error('Failed to load latest news:', newsResult.error);
                }

            } catch (error) {
                console.error('Failed to load homepage data:', error);
                // 如果API调用失败，显示默认提示
                this.stats = {
                    totalPosts: '请先登录',
                    totalComments: '请先登录',
                    totalSchools: '请先登录',
                    totalTasks: '请先登录'
                };
            } finally {
                this.loading = false;
            }
        }
    }
};

// 登录组件
const LoginPage = {
    template: `
        <div class="auth-form">
            <h2 class="text-center mb-4">用户登录</h2>
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <form @submit.prevent="login">
                <div class="mb-3">
                    <label for="username" class="form-label">用户名</label>
                    <input type="text" class="form-control" id="username" v-model="username" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">密码</label>
                    <input type="password" class="form-control" id="password" v-model="password" required>
                </div>
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary" :disabled="loading">
                        <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                        登录
                    </button>
                </div>
                <div class="text-center mt-3">
                    <p>还没有账号？ <a @click.prevent="$parent.navigateTo('/register')" style="cursor: pointer;">立即注册</a></p>
                </div>
            </form>
        </div>
    `,
    emits: ['login'],
    data() {
        return {
            username: '',
            password: '',
            loading: false,
            error: null
        }
    },
    methods: {
        async login() {
            this.loading = true;
            this.error = null;

            try {
                // 调用登录API
                const result = await API.auth.login(this.username, this.password);

                if (result.success) {
                    console.log('登录API成功，设置token:', result.data.access_token.substring(0, 10) + '...');

                    // 设置token到axios和localStorage
                    API.setToken(result.data.access_token);

                    // 获取用户信息
                    const userResult = await API.auth.getCurrentUser();

                    if (userResult.success) {
                        // 存储用户数据和token
                        const userData = userResult.data;
                        userData.token = result.data.access_token; // 确保token一起传递

                        console.log('登录成功，用户数据:', userData.username);

                        // 触发登录事件，将用户数据传递给父组件
                        this.$emit('login', userData);
                    } else {
                        this.error = '获取用户信息失败: ' + (userResult.error?.message || '未知错误');
                        console.error('获取用户信息失败:', userResult.error);
                        // 清除token
                        API.setToken(null);
                    }
                } else {
                    this.error = result.error.message || '登录失败，请检查用户名和密码';
                    console.error('登录失败:', result.error);
                }
            } catch (error) {
                console.error('登录过程中发生异常:', error);
                this.error = '登录过程中发生异常，请稍后再试';
                // 清除可能部分设置的token
                API.setToken(null);
            } finally {
                this.loading = false;
            }
        }
    }
};

// 注册组件
const RegisterPage = {
    template: `
        <div class="auth-form">
            <h2 class="text-center mb-4">用户注册</h2>
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div v-if="success" class="alert alert-success">{{ success }}</div>
            <form @submit.prevent="register">
                <div class="mb-3">
                    <label for="username" class="form-label">用户名</label>
                    <input type="text" class="form-control" id="username" v-model="username" required minlength="3">
                    <div class="form-text">用户名长度3-50个字符</div>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">电子邮箱</label>
                    <input type="email" class="form-control" id="email" v-model="email" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">密码</label>
                    <input type="password" class="form-control" id="password" v-model="password" required minlength="6">
                    <div class="form-text">密码至少6个字符</div>
                </div>
                <div class="mb-3">
                    <label for="confirmPassword" class="form-label">确认密码</label>
                    <input type="password" class="form-control" id="confirmPassword" v-model="confirmPassword" required>
                </div>
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary" :disabled="loading || password !== confirmPassword">
                        <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                        注册
                    </button>
                </div>
                <div class="text-center mt-3">
                    <p>已有账号？ <a href="/login">立即登录</a></p>
                </div>
            </form>
        </div>
    `,
    emits: ['register'],
    data() {
        return {
            username: '',
            email: '',
            password: '',
            confirmPassword: '',
            loading: false,
            error: null,
            success: null
        }
    },
    methods: {
        async register() {
            if (this.password !== this.confirmPassword) {
                this.error = '两次输入的密码不一致';
                return;
            }

            this.loading = true;
            this.error = null;
            this.success = null;

            const result = await API.auth.register(this.username, this.password, this.email);

            if (result.success) {
                this.success = '注册成功！3秒后跳转到登录页面...';
                this.$emit('register', result.data);

                // 清空表单
                this.username = '';
                this.email = '';
                this.password = '';
                this.confirmPassword = '';

                // 3秒后跳转到登录页面
                setTimeout(() => {
                    window.location.href = '/login';
                }, 3000);
            } else {
                this.error = result.error.message || '注册失败，请稍后再试';
            }

            this.loading = false;
        }
    }
};

// 帖子列表组件
const PostsPage = {
    template: `
        <div>
            <h2 class="mb-4">高校数据</h2>
            
            <div class="row mb-4">
                <div class="col-md-8">
                    <div class="input-group">
                        <input type="text" class="form-control" placeholder="搜索关键词..." v-model="keyword">
                        <button class="btn btn-primary" type="button" @click="searchPosts">搜索</button>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="d-flex justify-content-end">
                        <select class="form-select" v-model="filter.tag" @change="filterPosts">
                            <option value="">所有标签</option>
                            <option v-for="tag in availableTags" :value="tag">{{ tag }}</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-2">加载数据中...</p>
            </div>
            
            <div v-else-if="posts && posts.length === 0" class="text-center py-5">
                <p class="text-muted">暂无数据</p>
            </div>
            
            <div v-else>
                <div class="card mb-4" v-for="post in posts" :key="post.id">
                    <div class="card-body">
                        <h5 class="card-title">{{ post.title }}</h5>
                        <h6 class="card-subtitle mb-2 text-muted">
                            <span>发布者: {{ post.poster }}</span>
                            <span class="ms-3">发布时间: {{ formatDate(post.time) }}</span>
                        </h6>
                        <p class="card-text">{{ truncateContent(post.content) }}</p>
                        <div class="mb-2">
                            <span v-for="tag in post.tags" :key="tag" class="badge bg-primary me-1">{{ tag }}</span>
                        </div>
                        <div class="d-flex justify-content-between">
                            <div>
                                <span class="me-3">
                                    <img src="/static/img/like.svg" alt="点赞" width="16" height="16" class="me-1">
                                    {{ post.like_count }} 点赞
                                </span>
                                <span class="me-3">
                                    <img src="/static/img/comment.svg" alt="评论" width="16" height="16" class="me-1">
                                    {{ post.comment_count }} 评论
                                </span>
                                <span>
                                    <img src="/static/img/collect.svg" alt="收藏" width="16" height="16" class="me-1">
                                    {{ post.collect_count }} 收藏
                                </span>
                            </div>
                            <button class="btn btn-sm btn-outline-primary" @click="showComments(post)">
                                {{ post.showComments ? '收起评论' : '查看评论' }}
                            </button>
                        </div>
                    </div>
                    
                    <div class="card-footer bg-light" v-if="post.showComments">
                        <h6>评论 ({{ post.comments.length }})</h6>
                        <div v-if="post.comments.length === 0" class="text-muted">暂无评论</div>
                        <div v-else class="comment-list">
                            <div class="comment-item p-2 border-bottom" v-for="comment in post.comments" :key="comment.id">
                                <div class="d-flex justify-content-between">
                                    <strong>{{ comment.commenter }}</strong>
                                    <small class="text-muted">{{ formatDate(comment.time) }}</small>
                                </div>
                                <p class="mb-1">{{ comment.content }}</p>
                                <div class="small">
                                    <span class="me-2"><i class="bi bi-heart"></i> {{ comment.like_count }}</span>
                                    <span><i class="bi bi-chat"></i> {{ comment.reply_count }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="me-2">共 {{ total }} 条数据</span>
                        <select class="form-select form-select-sm d-inline-block w-auto" v-model="pageSize" @change="loadPosts">
                            <option value="10">10条/页</option>
                            <option value="20">20条/页</option>
                            <option value="50">50条/页</option>
                        </select>
                    </div>
                    
                    <nav aria-label="Page navigation">
                        <ul class="pagination">
                            <li class="page-item" :class="{ disabled: currentPage === 1 }">
                                <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">上一页</a>
                            </li>
                            <li class="page-item" v-for="page in totalPages" :key="page" :class="{ active: page === currentPage }">
                                <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
                            </li>
                            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                                <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">下一页</a>
                            </li>
                        </ul>
                    </nav>
                </div>
            </div>
        </div>
    `,
    props: ['user'],
    data() {
        return {
            posts: [],
            loading: true,
            keyword: '',
            filter: {
                tag: '',
                min_likes: null
            },
            currentPage: 1,
            pageSize: 20,
            total: 0,
            availableTags: []
        }
    },
    computed: {
        totalPages() {
            return Math.ceil(this.total / this.pageSize);
        }
    },
    mounted() {
        this.loadPosts();
    },
    methods: {
        async loadPosts() {
            this.loading = true;

            const params = {
                skip: (this.currentPage - 1) * this.pageSize,
                limit: this.pageSize,
                keyword: this.keyword || undefined,
                tag: this.filter.tag || undefined,
                min_likes: this.filter.min_likes || undefined
            };

            const result = await API.posts.getPosts(params);

            if (result.success) {
                this.posts = result.data.posts.map(post => ({
                    ...post,
                    showComments: false
                }));
                this.total = result.data.total;

                // 收集所有可用的标签
                const tags = new Set();
                this.posts.forEach(post => {
                    post.tags.forEach(tag => tags.add(tag));
                });
                this.availableTags = [...tags];
            } else {
                console.error('Failed to load posts:', result.error);
            }

            this.loading = false;
        },

        showComments(post) {
            post.showComments = !post.showComments;
        },

        searchPosts() {
            this.currentPage = 1;
            this.loadPosts();
        },

        filterPosts() {
            this.currentPage = 1;
            this.loadPosts();
        },

        changePage(page) {
            if (page < 1 || page > this.totalPages) {
                return;
            }
            this.currentPage = page;
            this.loadPosts();
        },

        formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        truncateContent(content) {
            if (!content) return '';
            return content.length > 200 ? content.substring(0, 200) + '...' : content;
        }
    }
};

// 爬虫任务列表组件
const TasksPage = {
    template: `
        <div>
            <h2 class="mb-4">爬虫任务管理</h2>
            
            <div class="row mb-4">
                <div class="col-md-8">
                    <div class="input-group">
                        <input type="text" class="form-control" placeholder="搜索关键词..." v-model="keyword">
                        <button class="btn btn-primary" type="button" @click="searchTasks">搜索</button>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="d-flex justify-content-end">
                        <select class="form-select" v-model="statusFilter" @change="filterTasks">
                            <option value="">所有状态</option>
                            <option value="completed">已完成</option>
                            <option value="running">运行中</option>
                            <option value="pending">等待中</option>
                            <option value="failed">失败</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-2">加载数据中...</p>
            </div>
            
            <div v-else-if="tasks && tasks.length === 0" class="text-center py-5">
                <p class="text-muted">暂无任务数据</p>
            </div>
            
            <div v-else>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-light">
                            <tr>
                                <th>任务ID</th>
                                <th>关键词</th>
                                <th>平台</th>
                                <th>状态</th>
                                <th>创建时间</th>
                                <th>完成时间</th>
                                <th>已收集帖子</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="task in tasks" :key="task.task_id">
                                <td>{{ task.task_id }}</td>
                                <td>{{ task.keyword }}</td>
                                <td>{{ getPlatformName(task.site) }}</td>
                                <td>
                                    <span class="status-badge" :class="'status-' + task.status">
                                        {{ getStatusText(task.status) }}
                                    </span>
                                </td>
                                <td>{{ formatDate(task.created_at) }}</td>
                                <td>{{ task.completed_at ? formatDate(task.completed_at) : '-' }}</td>
                                <td>{{ task.posts_collected }}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-info" @click="viewTaskDetail(task.task_id)">
                                        详情
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="me-2">共 {{ total }} 条数据</span>
                        <select class="form-select form-select-sm d-inline-block w-auto" v-model="pageSize" @change="loadTasks">
                            <option value="10">10条/页</option>
                            <option value="20">20条/页</option>
                            <option value="50">50条/页</option>
                        </select>
                    </div>
                    
                    <nav aria-label="Page navigation">
                        <ul class="pagination">
                            <li class="page-item" :class="{ disabled: currentPage === 1 }">
                                <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">上一页</a>
                            </li>
                            <li class="page-item" v-for="page in totalPages" :key="page" :class="{ active: page === currentPage }">
                                <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
                            </li>
                            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                                <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">下一页</a>
                            </li>
                        </ul>
                    </nav>
                </div>
            </div>
            
            <!-- 任务详情模态框 -->
            <div class="modal fade" id="taskDetailModal" tabindex="-1" aria-labelledby="taskDetailModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="taskDetailModalLabel">任务详情</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div v-if="taskDetail">
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <p><strong>任务ID:</strong> {{ taskDetail.task_id }}</p>
                                        <p><strong>关键词:</strong> {{ taskDetail.keyword }}</p>
                                        <p><strong>平台:</strong> {{ getPlatformName(taskDetail.site) }}</p>
                                        <p><strong>状态:</strong> 
                                            <span class="status-badge" :class="'status-' + taskDetail.status">
                                                {{ getStatusText(taskDetail.status) }}
                                            </span>
                                        </p>
                                    </div>
                                    <div class="col-md-6">
                                        <p><strong>创建时间:</strong> {{ formatDate(taskDetail.created_at) }}</p>
                                        <p><strong>完成时间:</strong> {{ taskDetail.completed_at ? formatDate(taskDetail.completed_at) : '-' }}</p>
                                        <p><strong>已收集帖子:</strong> {{ taskDetail.posts_collected }}</p>
                                        <p><strong>请求帖子数:</strong> {{ taskDetail.post_count }}</p>
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <p><strong>包含评论:</strong> {{ taskDetail.include_comments ? '是' : '否' }}</p>
                                        <p><strong>每帖评论数:</strong> {{ taskDetail.comments_per_post }}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <p><strong>最低点赞数:</strong> {{ taskDetail.min_likes }}</p>
                                        <p><strong>评论最低点赞数:</strong> {{ taskDetail.comment_min_likes }}</p>
                                        <p><strong>包含图片:</strong> {{ taskDetail.include_images ? '是' : '否' }}</p>
                                    </div>
                                </div>
                                <div v-if="taskDetail.error_message" class="alert alert-danger">
                                    <strong>错误信息:</strong> {{ taskDetail.error_message }}
                                </div>
                            </div>
                            <div v-else class="text-center py-3">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">加载中...</span>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    props: ['user'],
    data() {
        return {
            tasks: [],
            loading: true,
            keyword: '',
            statusFilter: '',
            currentPage: 1,
            pageSize: 20,
            total: 0,
            taskDetail: null,
            taskDetailModal: null
        }
    },
    computed: {
        totalPages() {
            return Math.ceil(this.total / this.pageSize);
        }
    },
    mounted() {
        this.loadTasks();
        this.taskDetailModal = new bootstrap.Modal(document.getElementById('taskDetailModal'));
    },
    methods: {
        async loadTasks() {
            this.loading = true;

            const params = {
                skip: (this.currentPage - 1) * this.pageSize,
                limit: this.pageSize,
                keyword: this.keyword || undefined,
                status: this.statusFilter || undefined
            };

            const result = await API.tasks.getTasks(params);

            if (result.success) {
                this.tasks = result.data.tasks;
                this.total = result.data.total;
            } else {
                console.error('Failed to load tasks:', result.error);
            }

            this.loading = false;
        },

        searchTasks() {
            this.currentPage = 1;
            this.loadTasks();
        },

        filterTasks() {
            this.currentPage = 1;
            this.loadTasks();
        },

        changePage(page) {
            if (page < 1 || page > this.totalPages) {
                return;
            }
            this.currentPage = page;
            this.loadTasks();
        },

        async viewTaskDetail(taskId) {
            this.taskDetail = null;
            this.taskDetailModal.show();

            const result = await API.tasks.getTaskDetail(taskId);

            if (result.success) {
                this.taskDetail = result.data;
            } else {
                console.error('Failed to load task detail:', result.error);
            }
        },

        formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        getPlatformName(siteId) {
            const platforms = {
                0: '小红书'
            };
            return platforms[siteId] || '未知平台';
        },

        getStatusText(status) {
            const statusText = {
                'completed': '已完成',
                'failed': '失败',
                'running': '运行中',
                'pending': '等待中',
                'divided': '已分解'
            };
            return statusText[status] || '未知状态';
        }
    }
};

// 爬虫启动组件
const CrawlerPage = {
    template: `
        <div>
            <h2 class="mb-4">启动爬虫任务</h2>
            
            <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
                {{ success }}
                <button type="button" class="btn-close" @click="success = null"></button>
            </div>
            
            <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
                {{ error }}
                <button type="button" class="btn-close" @click="error = null"></button>
            </div>
            
            <div class="card">
                <div class="card-body">
                    <form @submit.prevent="startCrawl">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label for="keyword" class="form-label">关键词</label>
                                <input type="text" class="form-control" id="keyword" v-model="formData.keyword" required>
                                <div class="form-text">例如: 高校名称+专业名称</div>
                            </div>
                            <div class="col-md-6">
                                <label for="site" class="form-label">目标平台</label>
                                <select class="form-select" id="site" v-model="formData.site" required>
                                    <option value="0">小红书</option>
                                </select>
                                <div class="form-text">目前只支持小红书平台</div>
                            </div>
                        </div>
                        
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label for="post_count" class="form-label">帖子数量</label>
                                <input type="number" class="form-control" id="post_count" v-model="formData.post_count" min="5" max="50" required>
                                <div class="form-text">爬取的帖子数量 (5-50)</div>
                            </div>
                            <div class="col-md-6">
                                <label for="min_likes" class="form-label">最低点赞数</label>
                                <input type="number" class="form-control" id="min_likes" v-model="formData.min_likes" min="0" required>
                                <div class="form-text">低于此数值的帖子将被过滤</div>
                            </div>
                        </div>
                        
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="include_comments" v-model="formData.include_comments">
                                    <label class="form-check-label" for="include_comments">包含评论</label>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="include_images" v-model="formData.include_images">
                                    <label class="form-check-label" for="include_images">包含图片URL</label>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row mb-3" v-if="formData.include_comments">
                            <div class="col-md-6">
                                <label for="comments_per_post" class="form-label">每帖评论数</label>
                                <input type="number" class="form-control" id="comments_per_post" v-model="formData.comments_per_post" min="1" max="30" required>
                                <div class="form-text">每个帖子获取的评论数量 (1-30)</div>
                            </div>
                            <div class="col-md-6">
                                <label for="comment_min_likes" class="form-label">评论最低点赞数</label>
                                <input type="number" class="form-control" id="comment_min_likes" v-model="formData.comment_min_likes" min="0" required>
                                <div class="form-text">低于此数值的评论将被过滤</div>
                            </div>
                        </div>
                        
                        <div class="alert alert-warning">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i>
                            提示: 爬虫任务可能需要一些时间才能完成，取决于数据量和网络状况。
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary" :disabled="loading">
                                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                                启动爬虫任务
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `,
    props: ['user'],
    emits: ['start-crawl'],
    data() {
        return {
            formData: {
                keyword: '',
                site: 0,
                post_count: 20,
                include_comments: true,
                min_likes: 0,
                comments_per_post: 10,
                comment_min_likes: 0,
                include_images: false
            },
            loading: false,
            error: null,
            success: null
        }
    },
    methods: {
        async startCrawl() {
            this.loading = true;
            this.error = null;
            this.success = null;

            // 将site转换为文字
            const crawlData = {
                ...this.formData,
                site: parseInt(this.formData.site)
            };

            const result = await API.crawler.startCrawl(crawlData);

            if (result.success) {
                this.success = `爬虫任务创建成功，任务ID: ${result.data.task_id}`;
                this.$emit('start-crawl', result.data);

                // 重置表单
                setTimeout(() => {
                    this.formData = {
                        keyword: '',
                        site: 0,
                        post_count: 20,
                        include_comments: true,
                        min_likes: 0,
                        comments_per_post: 10,
                        comment_min_likes: 0,
                        include_images: false
                    };
                }, 2000);
            } else {
                this.error = result.error.message || '启动爬虫任务失败';
            }

            this.loading = false;
        }
    }
};

// 导出所有组件
const components = {
    HomePage,
    LoginPage,
    RegisterPage,
    PostsPage,
    TasksPage,
    CrawlerPage
};
