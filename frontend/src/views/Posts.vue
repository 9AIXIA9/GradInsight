<template>
  <div class="container-fluid">
    <!-- 标题栏 -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-0"><i class="bi bi-postcard me-2"></i>高校数据浏览</h2>
        <p class="text-muted mt-1">浏览从小红书爬取的高校相关帖子和评论</p>
      </div>
      <div class="d-flex gap-2">
        <div class="btn-group btn-group-sm">
          <input type="radio" class="btn-check" name="vm" id="vgrid" v-model="viewMode" value="grid">
          <label class="btn btn-outline-primary" for="vgrid"><i class="bi bi-grid-3x3-gap"></i></label>
          <input type="radio" class="btn-check" name="vm" id="vlist" v-model="viewMode" value="list">
          <label class="btn btn-outline-primary" for="vlist"><i class="bi bi-list"></i></label>
        </div>
        <div class="input-group" style="width:280px">
          <input v-model="searchKeyword" type="text" class="form-control" placeholder="搜索关键词..." @keyup.enter="loadPosts">
          <button class="btn btn-primary" @click="loadPosts"><i class="bi bi-search"></i></button>
        </div>
      </div>
    </div>

    <!-- 筛选条 -->
    <div class="row g-2 mb-4">
      <div class="col-auto"><input v-model.number="filters.min_likes" type="number" class="form-control" placeholder="最小点赞" @change="loadPosts" style="width:110px"></div>
      <div class="col-auto"><input v-model.number="filters.min_comments" type="number" class="form-control" placeholder="最小评论" @change="loadPosts" style="width:110px"></div>
      <div class="col-auto"><select v-model="sortConfig.field" class="form-select" @change="loadPosts" style="width:130px">
        <option value="time">按时间</option><option value="like_count">按点赞</option><option value="comment_count">按评论</option><option value="collect_count">按收藏</option><option value="hot_score">按热度</option>
      </select></div>
      <div class="col-auto"><select v-model="sortConfig.order" class="form-select" @change="loadPosts" style="width:100px">
        <option value="desc">降序</option><option value="asc">升序</option>
      </select></div>
      <div class="col-auto"><button class="btn btn-outline-secondary btn-sm" @click="resetFilters"><i class="bi bi-arrow-clockwise me-1"></i>重置</button></div>
      <div class="col text-end"><span class="text-muted">共 {{ posts.total || 0 }} 条</span></div>
    </div>

    <!-- 加载 -->
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div><p class="mt-3 text-muted">加载中...</p></div>

    <!-- 网格视图 -->
    <div v-else-if="viewMode === 'grid'" class="row">
      <div v-for="post in posts.items" :key="post.id" class="col-xl-3 col-lg-4 col-md-6 mb-4">
        <div class="card h-100 shadow-sm post-card" @click="viewPostDetails(post)" style="cursor:pointer">
          <!-- 首图 -->
          <div class="card-img-container" :style="!getImages(post).length ? {background: gradientBg(post.id)} : {}">
            <img referrerpolicy="no-referrer" crossorigin="anonymous" v-if="getImages(post).length" :src="proxyUrl(getImages(post)[0])" class="card-img-top post-thumb" alt="" @error="onImgError($event)" loading="lazy">
            <div v-if="!getImages(post).length" class="card-img-placeholder"><i class="bi bi-card-image" style="font-size:2.5rem;opacity:0.3"></i></div>
            <div v-if="getImages(post).length>1" class="position-absolute bottom-0 end-0 m-1 bg-dark bg-opacity-50 text-white rounded px-1 small">{{ getImages(post).length }}图</div>
            <span class="badge bg-primary position-absolute top-0 start-0 m-2">小红书</span>
            <span v-if="post.hot_score > 0" class="badge bg-danger position-absolute top-0 end-0 m-2">🔥 {{ (post.hot_score||0).toFixed(1) }}</span>
          </div>
          <div class="card-body d-flex flex-column">
            <h6 class="card-title text-truncate-2">{{ getDisplayTitle(post) }}</h6>
            <p class="card-text text-muted small flex-grow-1">{{ truncateText(post.content, 80) }}</p>
            <!-- 标签 -->
            <div v-if="getTags(post).length" class="mb-2">
              <span v-for="tag in getTags(post).slice(0,3)" :key="tag" class="badge bg-light text-dark me-1 mb-1">#{{ tag }}</span>
            </div>
            <div class="d-flex justify-content-between align-items-center mt-auto">
              <small class="text-muted"><i class="bi bi-person me-1"></i>{{ post.poster || '匿名' }}</small>
              <small class="text-muted">{{ formatDate(post.time || post.created_at) }}</small>
            </div>
            <div class="d-flex justify-content-around mt-2 pt-2 border-top">
              <span class="text-muted small"><i class="bi bi-heart text-danger me-1"></i>{{ formatNumber(post.like_count) }}</span>
              <span class="text-muted small"><i class="bi bi-chat text-success me-1"></i>{{ formatNumber(post.comment_count) }}</span>
              <span class="text-muted small"><i class="bi bi-bookmark text-warning me-1"></i>{{ formatNumber(post.collect_count) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 列表视图 -->
    <div v-else class="card">
      <div class="list-group list-group-flush">
        <div v-for="post in posts.items" :key="post.id" class="list-group-item p-3 post-item" @click="viewPostDetails(post)" style="cursor:pointer">
          <div class="row g-3">
            <div class="col-auto" style="width:120px">
              <img referrerpolicy="no-referrer" crossorigin="anonymous" v-if="getImages(post).length" :src="proxyUrl(getImages(post)[0])" class="rounded" style="width:120px;height:90px;object-fit:cover" alt="" @error="onImgError($event)" loading="lazy">
              <div v-else class="rounded d-flex align-items-center justify-content-center" :style="{background:gradientBg(post.id)}" style="width:120px;height:90px"><i class="bi bi-card-image" style="font-size:1.5rem;opacity:0.3"></i></div>
            </div>
            <div class="col">
              <div class="d-flex justify-content-between align-items-start">
                <h6 class="mb-1">{{ getDisplayTitle(post) }}</h6>
                <small class="text-muted text-nowrap ms-2">{{ formatDate(post.time || post.created_at) }}</small>
              </div>
              <p class="mb-1 text-muted small">{{ truncateText(post.content, 120) }}</p>
              <div class="d-flex gap-3 mt-2">
                <small class="text-muted"><i class="bi bi-person me-1"></i>{{ post.poster || '匿名' }}</small>
                <small class="text-muted"><i class="bi bi-heart text-danger me-1"></i>{{ formatNumber(post.like_count) }}</small>
                <small class="text-muted"><i class="bi bi-chat text-success me-1"></i>{{ formatNumber(post.comment_count) }}</small>
                <small class="text-muted"><i class="bi bi-bookmark text-warning me-1"></i>{{ formatNumber(post.collect_count) }}</small>
                <small v-if="post.hot_score>0" class="text-muted"><i class="bi bi-fire text-danger me-1"></i>{{ (post.hot_score||0).toFixed(1) }}</small>
              </div>
              <div v-if="getTags(post).length" class="mt-1">
                <span v-for="tag in getTags(post).slice(0,5)" :key="tag" class="badge bg-light text-dark me-1">#{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <nav v-if="posts.total > pagination.pageSize" class="mt-4">
      <ul class="pagination justify-content-center">
        <li class="page-item" :class="{disabled:pagination.currentPage===1}"><button class="page-link" @click="changePage(1)">首页</button></li>
        <li class="page-item" :class="{disabled:pagination.currentPage===1}"><button class="page-link" @click="changePage(pagination.currentPage-1)"><i class="bi bi-chevron-left"></i></button></li>
        <li v-for="p in visiblePages" :key="p" class="page-item" :class="{active:p===pagination.currentPage}"><button class="page-link" @click="changePage(p)">{{ p }}</button></li>
        <li class="page-item" :class="{disabled:pagination.currentPage===totalPages}"><button class="page-link" @click="changePage(pagination.currentPage+1)"><i class="bi bi-chevron-right"></i></button></li>
        <li class="page-item" :class="{disabled:pagination.currentPage===totalPages}"><button class="page-link" @click="changePage(totalPages)">末页</button></li>
      </ul>
    </nav>

    <!-- 详情模态框 -->
    <div class="modal fade" :class="{show:showDetailsModal}" :style="{display:showDetailsModal?'block':'none'}" @click.self="showDetailsModal=false">
      <div class="modal-dialog modal-xl modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title"><i class="bi bi-postcard me-2"></i>{{ getDisplayTitle(selectedPost) }}</h5><button class="btn-close" @click="showDetailsModal=false"></button></div>
          <div class="modal-body" v-if="selectedPost">
            <div class="row">
              <div class="col-lg-8">
                <!-- 图片轮播 -->
                <div v-if="getImages(selectedPost).length" class="mb-4">
                  <div id="postCarousel" class="carousel slide" data-bs-ride="false">
                    <div class="carousel-inner rounded" style="background:#f1f1f1">
                      <div v-for="(img, idx) in getImages(selectedPost)" :key="idx" class="carousel-item" :class="{active:idx===0}">
                        <img referrerpolicy="no-referrer" crossorigin="anonymous" :src="proxyUrl(img)" class="d-block mx-auto" style="max-height:500px;object-fit:contain" alt="" loading="lazy">
                      </div>
                    </div>
                    <button v-if="getImages(selectedPost).length>1" class="carousel-control-prev" type="button" @click.stop="carouselPrev">
                      <span class="carousel-control-prev-icon"></span></button>
                    <button v-if="getImages(selectedPost).length>1" class="carousel-control-next" type="button" @click.stop="carouselNext">
                      <span class="carousel-control-next-icon"></span></button>
                  </div>
                  <div class="d-flex gap-1 mt-2 overflow-auto">
                    <img referrerpolicy="no-referrer" crossorigin="anonymous" v-for="(img, idx) in getImages(selectedPost)" :key="idx" :src="proxyUrl(img)" class="rounded" style="width:60px;height:60px;object-fit:cover;cursor:pointer;border:2px solid transparent" :style="{borderColor: activeImageIdx===idx ? '#0d6efd' : 'transparent'}" @click="activeImageIdx=idx" loading="lazy">
                  </div>
                </div>
                <!-- 帖子内容 -->
                <div class="mb-3"><span class="badge bg-primary me-2">小红书</span><span v-if="selectedPost.hot_score>0" class="badge bg-danger me-2">🔥 {{ (selectedPost.hot_score||0).toFixed(1) }}</span><small class="text-muted">{{ formatDate(selectedPost.time || selectedPost.created_at) }}</small></div>
                <div class="d-flex gap-2 mb-3"><small class="text-muted"><i class="bi bi-person me-1"></i>{{ selectedPost.poster || '匿名' }}</small><small v-if="selectedPost.location" class="text-muted"><i class="bi bi-geo-alt me-1"></i>{{ selectedPost.location }}</small></div>
                <div v-if="getTags(selectedPost).length" class="mb-3"><span v-for="tag in getTags(selectedPost)" :key="tag" class="badge bg-light text-dark me-1">#{{ tag }}</span></div>
                <div class="post-content p-3 bg-light rounded mb-3" style="white-space:pre-wrap;line-height:1.8">{{ selectedPost.content }}</div>
                <div class="row text-center mb-4">
                  <div class="col-4"><div class="border rounded p-2"><i class="bi bi-heart-fill text-danger me-1"></i><strong>{{ formatNumber(selectedPost.like_count) }}</strong><br><small class="text-muted">点赞</small></div></div>
                  <div class="col-4"><div class="border rounded p-2"><i class="bi bi-chat-fill text-success me-1"></i><strong>{{ formatNumber(selectedPost.comment_count) }}</strong><br><small class="text-muted">评论</small></div></div>
                  <div class="col-4"><div class="border rounded p-2"><i class="bi bi-bookmark-fill text-warning me-1"></i><strong>{{ formatNumber(selectedPost.collect_count) }}</strong><br><small class="text-muted">收藏</small></div></div>
                </div>
              </div>
              <div class="col-lg-4">
                <!-- 评论 -->
                <h6><i class="bi bi-chat-dots me-2"></i>评论 ({{ getComments(selectedPost).length }})</h6>
                <div v-if="getComments(selectedPost).length" class="comments-scroll" style="max-height:60vh;overflow-y:auto">
                  <div v-for="c in getComments(selectedPost)" :key="c.id" class="border rounded p-2 mb-2 bg-light">
                    <div class="d-flex justify-content-between"><strong class="small">{{ c.commenter || '匿名' }}</strong><small class="text-muted">{{ formatDate(c.time) }}</small></div>
                    <p class="mb-1 small mt-1">{{ c.content }}</p>
                    <small class="text-muted"><i class="bi bi-heart me-1"></i>{{ c.like_count||0 }} <i class="bi bi-reply ms-2 me-1"></i>{{ c.reply_count||0 }}</small>
                  </div>
                </div>
                <div v-else class="text-center text-muted py-4"><i class="bi bi-chat display-6"></i><p>暂无评论</p></div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <a v-if="selectedPost?.link" :href="selectedPost.link" target="_blank" class="btn btn-primary me-auto"><i class="bi bi-box-arrow-up-right me-1"></i>查看原文</a>
            <button class="btn btn-secondary" @click="showDetailsModal=false">关闭</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showDetailsModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import apiClient from '@/services/apiClient'
import { computed, onMounted, reactive, ref } from 'vue'

const loading = ref(false)
const error = ref('')
const posts = ref({ items: [], total: 0 })
const searchKeyword = ref('')
const viewMode = ref('grid')
const showDetailsModal = ref(false)
const selectedPost = ref(null)
const activeImageIdx = ref(0)

const filters = reactive({ min_likes: '', min_comments: '' })
const sortConfig = reactive({ field: 'time', order: 'desc' })
const pagination = reactive({ currentPage: 1, pageSize: 20 })

const totalPages = computed(() => Math.max(1, Math.ceil(posts.value.total / pagination.pageSize)))
const visiblePages = computed(() => {
  let s = Math.max(1, pagination.currentPage - 2)
  let e = Math.min(totalPages.value, pagination.currentPage + 2)
  return Array.from({ length: e - s + 1 }, (_, i) => s + i)
})

function proxyUrl(url) { return "/api/posts/image-proxy?url=" + encodeURIComponent(url) }
function getImages(post) {
  if (!post?.image_urls) return []
  if (Array.isArray(post.image_urls)) return post.image_urls.filter(u => u)
  if (typeof post.image_urls === 'string') {
    try { return JSON.parse(post.image_urls).filter(u => u) } catch { return [] }
  }
  return []
}
function getTags(post) {
  if (!post?.tags) return []
  if (Array.isArray(post.tags)) return post.tags
  if (typeof post.tags === 'string') {
    try { return JSON.parse(post.tags) } catch { return post.tags.split(/[,#]/) }
  }
  return []
}
function getComments(post) {
  if (!post?.comments) return []
  if (Array.isArray(post.comments)) return post.comments
  return []
}

function carouselPrev() { const el = document.querySelector('#postCarousel'); if (el) new bootstrap.Carousel(el).prev() }
function carouselNext() { const el = document.querySelector('#postCarousel'); if (el) new bootstrap.Carousel(el).next() }

const loadPosts = async () => {
  loading.value = true; error.value = ''
  try {
    const params = { skip: (pagination.currentPage - 1) * pagination.pageSize, limit: pagination.pageSize, sort_by: sortConfig.field, sort_order: sortConfig.order }
    if (searchKeyword.value) params.keyword = searchKeyword.value
    if (filters.min_likes) params.min_likes = filters.min_likes
    if (filters.min_comments) params.min_comments = filters.min_comments
    const r = await apiClient.get('/api/posts', { params })
    if (r.success) posts.value = { items: r.data.posts || [], total: r.data.total || 0 }
    else error.value = r.error?.message || '加载失败'
  } catch (err) { error.value = '网络错误'; console.error(err) }
  finally { loading.value = false }
}

const resetFilters = () => { filters.min_likes = ''; filters.min_comments = ''; searchKeyword.value = ''; sortConfig.field = 'time'; sortConfig.order = 'desc'; pagination.currentPage = 1; loadPosts() }
const changePage = (p) => { if (p >= 1 && p <= totalPages.value) { pagination.currentPage = p; loadPosts() } }
const viewPostDetails = (post) => { selectedPost.value = post; activeImageIdx.value = 0; showDetailsModal.value = true }

const formatDate = (d) => { if (!d) return ''; return new Date(d).toLocaleDateString('zh-CN', { year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit' }) }
const truncateText = (t, n) => { if (!t) return ''; return t.length <= n ? t : t.slice(0, n) + '...' }
const formatNumber = (n) => { n = n || 0; if (n >= 10000) return (n/10000).toFixed(1)+'w'; if (n >= 1000) return (n/1000).toFixed(1)+'k'; return String(n) }
const onImgError = (e) => {
  const parent = e.target.parentElement
  e.target.remove()
  parent.classList.add('no-image')
  parent.style.background = gradientBg('err')
  const icon = document.createElement('div')
  icon.className = 'card-img-placeholder'
  icon.innerHTML = '<i class="bi bi-image" style="font-size:2.5rem;opacity:0.3"></i>'
  parent.prepend(icon)
}
const gradientBg = (seed) => {
  const hues = ['200,70%,85%','280,60%,90%','160,60%,88%','30,80%,88%','340,70%,90%','45,75%,88%']
  const idx = (typeof seed==='string' ? seed.charCodeAt(0)||0 : 0) % hues.length
  return `linear-gradient(135deg, hsl(${hues[idx]}), hsl(${hues[(idx+3)%hues.length]}))`
}

const getDisplayTitle = (post) => {
  if (post?.title?.trim()) return post.title.trim()
  if (post?.content?.trim()) return post.content.replace(/[\n\r#]/g, ' ').trim().slice(0, 30) + '...'
  return '无标题'
}

onMounted(() => { if (typeof bootstrap === 'undefined') { const s = document.createElement('script'); s.src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'; document.head.appendChild(s) } loadPosts() })
</script>

<style scoped>
.card-img-container { position:relative; overflow:hidden; height:180px; background:#f0f0f0; transition:background .3s }
.card-img-container.no-image { background:linear-gradient(135deg,#e8e8f0,#d8e0e8) !important }
.post-thumb { width:100%; height:100%; object-fit:cover }
.card-img-placeholder { width:100%; height:100%; display:flex; align-items:center; justify-content:center; position:absolute; top:0; left:0 }
.post-card { transition: transform .2s, box-shadow .2s; border-radius:12px; overflow:hidden }
.post-card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,.12) !important }
.post-item { transition: background .15s }
.post-item:hover { background: #f8f9fa }
.text-truncate-2 { display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden }
.comments-scroll::-webkit-scrollbar { width:4px }
.comments-scroll::-webkit-scrollbar-thumb { background:#ccc; border-radius:2px }
.modal.show { display:block !important }
</style>
