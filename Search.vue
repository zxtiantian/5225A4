<template>
  <div class="search-container">
    <el-card class="search-card">
      <template #header>
        <div class="card-header">
          <div class="header-content">
            <el-button
              type="primary"
              link
              @click="$router.push('/home')"
              class="back-button"
            >
              <el-icon><ArrowLeft /></el-icon>
              Back to Home
            </el-button>
            <h2>Search Bird Media Files</h2>
          </div>
        </div>
      </template>

      <!-- 精简版批量操作栏 -->
      <div v-if="selectedResults.length > 0" class="bulk-bar-simple">
        <el-input v-model="bulkTagName" placeholder="Tag name" style="width:120px;margin-right:8px" size="small" />
        <el-input-number v-model="bulkTagCount" :min="1" style="width:80px;margin-right:8px" size="small" />
        <el-button type="primary" size="small" @click="handleBulkTag" :disabled="!bulkTagName">Add Tag</el-button>
        <el-button type="danger" size="small" @click="handleBulkDelete">Delete</el-button>
      </div>

      <!-- 标签+数量搜索 -->
      <el-divider>Search by Tags & Count</el-divider>
      <el-form :inline="true" class="tags-form">
        <el-form-item v-for="(tag, i) in searchForm.tags" :key="i" label="Tag">
          <el-input-group>
            <el-input v-model="tag.name" placeholder="Tag name" style="width:120px" />
            <el-input-number v-model="tag.count" :min="1" controls-position="right" style="width:100px;margin-left:8px" />
            <el-button @click="removeTagField(i)" v-if="searchForm.tags.length>1" circle size="small" type="danger" class="tag-remove-btn">
              <el-icon><Delete /></el-icon>
            </el-button>
          </el-input-group>
        </el-form-item>
        <el-form-item>
          <el-button @click="addTagField" size="small" type="success" class="tag-add-btn">
            <el-icon><Plus /></el-icon> Add Tag
          </el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchByTags">Search</el-button>
        </el-form-item>
      </el-form>

      <!-- 物种名搜索 -->
      <el-divider>Search by Species</el-divider>
      <el-form :inline="true">
        <el-form-item label="Species (comma separated)">
          <el-input v-model="searchForm.species" placeholder="e.g. crow,pigeon" style="width:300px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchBySpecies">Search</el-button>
        </el-form-item>
      </el-form>

      <!-- 缩略图查原图 -->
      <!-- <el-divider>Find Full Image by Thumbnail URL</el-divider>
      <el-form :inline="true">
        <el-form-item label="Thumbnail URL">
          <el-input v-model="searchForm.thumbnail" placeholder="Paste thumbnail S3 URL here" style="width:400px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchByThumbnail">Query</el-button>
        </el-form-item>
      </el-form> -->
      <el-dialog v-model="showFullImage" title="Full Image Preview" width="600px" @close="closeFullImage">
        <el-image v-if="fullImageUrl" :src="fullImageUrl" fit="contain" style="width:100%" />
      </el-dialog>

      <!-- 批量标签添加栏 -->
      <div v-if="searchResults.length > 0" class="bulk-bar-multi">
        <div class="bulk-tags-list">
          <div v-for="(tag, i) in bulkTags" :key="i" class="bulk-tag-row">
            <el-input v-model="tag.name" placeholder="Tag name" style="width:120px;margin-right:8px" size="small" />
            <el-input-number v-model="tag.count" :min="1" style="width:80px;margin-right:8px" size="small" />
            <el-button @click="removeBulkTag(i)" circle size="small" type="danger" class="tag-remove-btn">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button @click="addBulkTag" size="small" type="success" class="tag-add-btn">
            <el-icon><Plus /></el-icon> Add Tag
          </el-button>
        </div>
        <el-button type="primary" size="small" @click="handleBulkTag" :disabled="selectedResults.length === 0" style="margin-left:16px">Add Tags to Selected</el-button>
        <el-button type="danger" size="small" @click="handleBulkDelete" :disabled="selectedResults.length === 0" style="margin-left:8px">Delete Selected</el-button>
      </div>

      <!-- 搜索结果展示 -->
      <el-divider>Search Results</el-divider>
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>
      <div v-else-if="searchResults.length > 0" class="search-results">
        <el-row :gutter="20">
          <el-col v-for="(item, idx) in searchResults" :key="item.url+idx" :xs="24" :sm="12" :md="8" :lg="6">
            <el-card class="result-card" shadow="hover">
              <div class="card-checkbox">
                <el-checkbox v-model="item._checked" @change="onSelectCard(item)" />
              </div>
              <template v-if="item.type === 'image'">
                <el-image :src="item.url" fit="cover" class="result-media" @click="handlePreview(item)" style="cursor:pointer" />
                <div class="detections-list">
                  <template v-if="item.detections && item.detections.length">
                    <div v-for="(group, i) in groupDetections(item.detections)" :key="i" class="detection-group">
                      <el-tag size="small" effect="dark" type="success">{{ group.name }}</el-tag>
                      <span class="detection-count">×{{ group.count }}</span>
                    </div>
                  </template>
                  <template v-else>
                    <span class="no-detection">No detections</span>
                  </template>
                </div>
              </template>
              <template v-else-if="item.type === 'video'">
                <div class="video-card" @click="handleVideoDownload(item)">
                  <Icon icon="mdi:movie-open" class="video-icon" />
                </div>
                <div class="detections-list">
                  <template v-if="item.detections && item.detections.length">
                    <template v-for="(group, i) in groupDetections(item.detections).slice(0,3)" :key="i">
                      <div class="detection-group">
                        <el-tag size="small" effect="dark" type="warning">{{ group.name }}</el-tag>
                        <span class="detection-count">×{{ group.count }}</span>
                      </div>
                    </template>
                    <span v-if="groupDetections(item.detections).length > 3" class="tag-ellipsis">...</span>
                  </template>
                  <template v-else>
                    <span class="no-detection">No detections</span>
                  </template>
                </div>
              </template>
              <template v-else-if="item.type === 'audio'">
                <div class="audio-card">
                  <el-icon class="audio-icon"><Headset /></el-icon>
                  <span class="audio-text">Audio</span>
                  <div class="audio-controls">
                    <el-button type="primary" circle @click.stop="playAudio(item)">
                      <el-icon><VideoPlay /></el-icon>
                    </el-button>
                  </div>
                </div>
                <div class="detections-list">
                  <template v-if="item.detections && item.detections.length">
                    <template v-for="(group, i) in groupDetections(item.detections).slice(0,3)" :key="i">
                      <div class="detection-group">
                        <el-tag size="small" effect="dark" type="info">{{ group.name }}</el-tag>
                        <span class="detection-count">×{{ group.count }}</span>
                      </div>
                    </template>
                    <span v-if="groupDetections(item.detections).length > 3" class="tag-ellipsis">...</span>
                  </template>
                  <template v-else>
                    <span class="no-detection">No detections</span>
                  </template>
                </div>
              </template>
            </el-card>
          </el-col>
        </el-row>
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[12, 24, 36, 48]"
            layout="total, sizes, prev, pager, next"
          />
        </div>
      </div>
      <div v-else class="empty-result">
        <el-empty description="No search results" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  ArrowLeft,
  Delete,
  Edit,
  Plus,
  VideoCameraFilled,
  Headset,
  VideoPlay
} from '@element-plus/icons-vue'
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'
import { getStsCredentials } from '../utils/s3Upload'
import { Icon } from '@iconify/vue'

const API_URLS = {
  search_by_tags: 'https://sjwjzoa9ib.execute-api.us-east-1.amazonaws.com/api/search_by_tags',
  search_by_species: 'https://ftfd6pgd5g.execute-api.us-east-1.amazonaws.com/api/search_by_species',
  full_image_by_thumbnail: 'https://efqfj17qv6.execute-api.us-east-1.amazonaws.com/api/full_image_by_thumbnail',
  bulk_tag: 'https://y6pt1mm5ce.execute-api.us-east-1.amazonaws.com/api/bulk_tag',
  bulk_delete: 'https://wm5uo0jk79.execute-api.us-east-1.amazonaws.com/api/bulk_delete',
}

const searchForm = reactive({
  tags: [{ name: '', count: 1 }],
  species: '',
  thumbnail: '',
  file: null,
  bulkUrls: '',
  bulkTags: [{ name: '', count: 1 }],
  bulkOp: 1,
  deleteUrls: ''
})
const loading = ref(false)
const searchResults = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const showFullImage = ref(false)
const fullImageUrl = ref('')
const bulkTagName = ref('')
const bulkTagCount = ref(1)
const bulkOp = ref(1)
const selectedResults = computed(() => searchResults.value.filter(item => item._checked))
const bulkTags = ref([{ name: '', count: 1 }])

// 添加 streamToBlob 辅助函数
const streamToBlob = async (stream, contentType) => {
  const chunks = []
  for await (const chunk of stream) {
    chunks.push(chunk)
  }
  return new Blob(chunks, { type: contentType })
}

async function getS3ImageUrl(s3url) {
  if (!s3url) return '';
  let bucket, key;
  if (s3url.startsWith('s3://')) {
    const url = s3url.replace('s3://', '');
    const firstSlash = url.indexOf('/');
    bucket = url.substring(0, firstSlash);
    key = url.substring(firstSlash + 1);
  } else if (s3url.startsWith('https://')) {
    const match = s3url.match(/^https:\/\/([^.]+)\.s3\.amazonaws.com\/(.+)$/);
    if (!match) return '';
    bucket = match[1];
    key = match[2];
  } else {
    return s3url;
  }
  const creds = await getStsCredentials();
  const s3 = new S3Client({
    region: 'us-east-1',
    credentials: {
      accessKeyId: creds.accessKeyId,
      secretAccessKey: creds.secretAccessKey,
      sessionToken: creds.sessionToken
    }
  });
  const command = new GetObjectCommand({
    Bucket: bucket,
    Key: key
  });
  const response = await s3.send(command);
  const reader = response.Body.getReader();
  const chunks = [];
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  const blob = new Blob(chunks, { type: response.ContentType || 'image/jpeg' });
  return URL.createObjectURL(blob);
}

// 查询：按标签+数量
async function searchByTags() {
  loading.value = true
  try {
    const tags = {}
    searchForm.tags.forEach(t => { if (t.name) tags[t.name] = t.count })
    const res = await fetch(API_URLS.search_by_tags, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tags })
    })
    const data = await res.json()
    searchResults.value = await Promise.all(
      (data.results || []).map(async item => {
        if (item.url.endsWith('.mp4')) {
          return { ...item, type: 'video', originUrl: item.url }
        } else {
          const isThumb = item.url.includes('/thumbnails/');
          const blobUrl = await getS3ImageUrl(item.url)
          return { ...item, url: blobUrl, originUrl: item.url, isThumb }
        }
      })
    )
    total.value = searchResults.value.length
  } catch (e) {
    ElMessage.error('Search failed')
  } finally {
    loading.value = false
  }
}
// 查询：按物种名
async function searchBySpecies() {
  loading.value = true
  try {
    const species = searchForm.species.split(',').map(s => s.trim()).filter(Boolean)
    const res = await fetch(API_URLS.search_by_species, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ species })
    })
    const data = await res.json()
    searchResults.value = await Promise.all(
      (data.results || []).map(async item => {
        if (item.url.endsWith('.mp4')) {
          return { ...item, type: 'video', originUrl: item.url }
        } else {
          const isThumb = item.url.includes('/thumbnails/');
          const blobUrl = await getS3ImageUrl(item.url)
          return { ...item, url: blobUrl, originUrl: item.url, isThumb }
        }
      })
    )
    total.value = searchResults.value.length
  } catch (e) {
    ElMessage.error('Search failed')
  } finally {
    loading.value = false
  }
}
// 查询：通过缩略图URL查原图
async function searchByThumbnail() {
  loading.value = true
  try {
    const res = await fetch(`${API_URLS.full_image_by_thumbnail}?thumbnail=${encodeURIComponent(searchForm.thumbnail)}`)
    const data = await res.json()
    if (data.fullImageUrl) {
      fullImageUrl.value = await getS3ImageUrl(data.fullImageUrl)
      showFullImage.value = true
    } else {
      ElMessage.warning('Not found')
    }
  } catch (e) {
    ElMessage.error('Query failed')
  } finally {
    loading.value = false
  }
}
// 查询：通过上传文件查同类文件（伪实现，需后端支持）
async function searchByFile() {
  ElMessage.info('请实现后端API后补充此功能')
}
// 批量加/删标签
async function bulkTag() {
  loading.value = true
  try {
    const urls = searchForm.bulkUrls.split('\n').map(u => u.trim()).filter(Boolean)
    const tags = searchForm.bulkTags.filter(t => t.name).map(t => `${t.name},${t.count}`)
    const res = await fetch(API_URLS.bulk_tag, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: urls, operation: searchForm.bulkOp, tags })
    })
    const data = await res.json()
    if (data.status === 'ok') ElMessage.success('操作成功')
    else ElMessage.error('操作失败')
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    loading.value = false
  }
}
// 批量删除
async function bulkDelete() {
  loading.value = true
  try {
    const urls = searchForm.deleteUrls.split('\n').map(u => u.trim()).filter(Boolean)
    const res = await fetch(API_URLS.bulk_delete, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls })
    })
    const data = await res.json()
    if (data.status === 'ok') ElMessage.success('删除成功')
    else ElMessage.error('删除失败')
  } catch (e) {
    ElMessage.error('删除失败')
  } finally {
    loading.value = false
  }
}
function addTagField() { searchForm.tags.push({ name: '', count: 1 }) }
function removeTagField(i) { if (searchForm.tags.length > 1) searchForm.tags.splice(i, 1) }
function addBulkTag() { bulkTags.value.push({ name: '', count: 1 }) }
function removeBulkTag(i) { if (bulkTags.value.length > 1) bulkTags.value.splice(i, 1) }
async function handlePreview(item) {
  // item: { url: blobUrl, type: 'image', originUrl: s3url, isThumb }
  if (item.isThumb && item.originUrl) {
    // 请求 full_image_by_thumbnail API
    const res = await fetch(`${API_URLS.full_image_by_thumbnail}?thumbnail=${encodeURIComponent(item.originUrl)}`);
    const data = await res.json();
    if (data.fullImageUrl) {
      // 这里 fullImageUrl 是 s3:// 路径
      fullImageUrl.value = await getS3ImageUrl(data.fullImageUrl);
    } else {
      fullImageUrl.value = item.url;
    }
    showFullImage.value = true;
  } else {
    fullImageUrl.value = item.url;
    showFullImage.value = true;
  }
}
function closeFullImage() { showFullImage.value = false; fullImageUrl.value = '' }

const dateShortcuts = [
  {
    text: 'Last week',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: 'Last month',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  },
  {
    text: 'Last 3 months',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    }
  }
]

const getMediaTypeLabel = (type) => {
  const labels = {
    image: 'Image',
    video: 'Video',
    audio: 'Audio'
  }
  return labels[type] || 'Unknown'
}

const getMediaTypeTagType = (type) => {
  const types = {
    image: 'success',
    video: 'warning',
    audio: 'info'
  }
  return types[type] || ''
}

const handleSearch = async () => {
  loading.value = true
  try {
    // 模拟搜索请求
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 根据媒体类型过滤结果
    let filteredResults = [...mockResults]
    if (searchForm.mediaType !== 'all') {
      filteredResults = mockResults.filter(item => item.mediaType === searchForm.mediaType)
    }
    
    searchResults.value = filteredResults
    total.value = filteredResults.length
  } catch (error) {
    console.error('Search error:', error)
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.mediaType = 'all'
  searchForm.dateRange = []
  currentPage.value = 1
  handleSearch()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  handleSearch()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  handleSearch()
}

function groupDetections(detections) {
  // 统计每种鸟的数量
  const map = {};
  detections.forEach(d => {
    if (!d.name) return;
    const key = d.name;
    map[key] = (map[key] || 0) + 1;
  });
  return Object.entries(map).map(([name, count]) => ({ name, count }));
}

function onSelectCard(item) {
  // 触发响应式
  item._checked = !!item._checked
}

async function handleBulkTag() {
  if (selectedResults.value.length === 0) return ElMessage.warning('No items selected')
  const tags = bulkTags.value.filter(t => t.name).map(t => `${t.name},${t.count}`)
  if (!tags.length) return ElMessage.warning('Please input at least one tag')
  loading.value = true
  try {
    const urls = selectedResults.value.map(item => item.originUrl || item.url)
    const res = await fetch(API_URLS.bulk_tag, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: urls, operation: 1, tags })
    })
    const data = await res.json()
    if (data.status === 'ok') {
      ElMessage.success('批量添加标签成功')
      await searchByTags() // 或 searchBySpecies
    } else {
      ElMessage.error('操作失败')
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    loading.value = false
  }
}

async function handleBulkDelete() {
  if (selectedResults.value.length === 0) return ElMessage.warning('No items selected')
  loading.value = true
  try {
    const urls = selectedResults.value.map(item => item.originUrl || item.url)
    const res = await fetch(API_URLS.bulk_delete, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls })
    })
    const data = await res.json()
    if (data.status === 'ok') {
      ElMessage.success('删除成功')
      await searchByTags() // 或 searchBySpecies，视当前tab
    } else {
      ElMessage.error('删除失败')
    }
  } catch (e) {
    ElMessage.error('删除失败')
  } finally {
    loading.value = false
  }
}

async function handleVideoDownload(item) {
  // item.url 是 blobUrl，item.originUrl 是 S3/https 路径
  try {
    let bucket, key;
    if (item.originUrl.startsWith('s3://')) {
      const url = item.originUrl.replace('s3://', '');
      const firstSlash = url.indexOf('/');
      bucket = url.substring(0, firstSlash);
      key = url.substring(firstSlash + 1);
    } else if (item.originUrl.startsWith('https://')) {
      const match = item.originUrl.match(/^https:\/\/([^.]+)\.s3\.amazonaws\.com\/(.+)$/);
      if (!match) return ElMessage.error('Invalid S3 URL');
      bucket = match[1];
      key = match[2];
    } else {
      return ElMessage.error('Invalid S3 URL');
    }
    const creds = await getStsCredentials();
    const s3 = new S3Client({
      region: 'us-east-1',
      credentials: {
        accessKeyId: creds.accessKeyId,
        secretAccessKey: creds.secretAccessKey,
        sessionToken: creds.sessionToken
      }
    });
    const command = new GetObjectCommand({ Bucket: bucket, Key: key });
    const response = await s3.send(command);
    const reader = response.Body.getReader();
    const chunks = [];
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
    }
    const blob = new Blob(chunks, { type: response.ContentType || 'video/mp4' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = key.split('/').pop();
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      URL.revokeObjectURL(url);
      document.body.removeChild(a);
    }, 1000);
  } catch (e) {
    ElMessage.error('Failed to download video');
  }
}

// 修改音频播放功能
const playAudio = async (result) => {
  try {
    const creds = await getStsCredentials()
    const s3 = new S3Client({
      region: 'us-east-1',
      credentials: {
        accessKeyId: creds.accessKeyId,
        secretAccessKey: creds.secretAccessKey,
        sessionToken: creds.sessionToken
      }
    })

    const command = new GetObjectCommand({
      Bucket: 'bird-recognition-files',
      Key: result.fileKey
    })

    const response = await s3.send(command)
    const blob = await streamToBlob(response.Body, response.ContentType || 'audio/wav')
    const url = URL.createObjectURL(blob)
    
    // 创建音频播放器
    const audio = new Audio(url)
    
    // 添加错误处理
    audio.onerror = (e) => {
      console.error('Audio playback error:', e)
      ElMessage.error('Failed to play audio file')
      URL.revokeObjectURL(url)
    }
    
    // 播放音频
    try {
      await audio.play()
    } catch (playError) {
      console.error('Error playing audio:', playError)
      ElMessage.error('Failed to play audio file')
      URL.revokeObjectURL(url)
    }
    
    // 清理 URL 对象
    audio.onended = () => {
      URL.revokeObjectURL(url)
    }
  } catch (error) {
    console.error('Error playing audio:', error)
    ElMessage.error('Failed to play audio')
  }
}

// 格式化时间戳
const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString()
}

// 初始加载
handleSearch()
</script>

<style scoped>
.search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.search-form {
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px;
}

.search-results {
  margin-top: 20px;
}

.result-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
  position: relative;
}

.result-card:hover {
  transform: translateY(-5px);
}

.result-media {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
}

.audio-preview {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.audio-icon {
  font-size: 48px;
  color: #909399;
  margin-bottom: 20px;
}

.result-audio {
  width: 90%;
}

.result-info {
  padding: 10px 0;
}

.result-info h3 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #303133;
}

.result-tags {
  margin: 10px 0;
}

.tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.result-details {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.confidence {
  margin: 5px 0;
  color: #67c23a;
}

.upload-time {
  margin: 5px 0;
}

.pagination-container {
  margin-top: 20px;
  text-align: center;
}

.empty-result {
  padding: 40px 0;
}

@media (max-width: 768px) {
  .search-form :deep(.el-form-item) {
    margin-bottom: 10px;
  }
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 5px;
}

.back-button .el-icon {
  margin-right: 4px;
}

.tags-form .el-form-item {
  margin-bottom: 12px;
  transition: background 0.2s;
}
.tags-form .el-form-item:hover {
  background: #f5f7fa;
  border-radius: 6px;
}
.tags-form .el-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.tags-form .el-input-number {
  min-width: 80px;
}
.tags-form .el-button[icon="el-icon-plus"] {
  font-weight: bold;
}
.tags-form .el-button[icon="el-icon-minus"] {
  color: #f56c6c;
}

.detections-list {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  min-height: 28px;
}
.detection-group {
  display: flex;
  align-items: center;
  background: #f0f9eb;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 13px;
}
.detection-count {
  color: #67c23a;
  margin-left: 4px;
  font-weight: bold;
}
.no-detection {
  color: #909399;
  font-size: 13px;
}

.bulk-bar-simple {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f5f7fa;
  border-radius: 6px;
  padding: 10px 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px #0001;
}

.bulk-bar-multi {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  background: #f5f7fa;
  border-radius: 6px;
  padding: 10px 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px #0001;
}
.bulk-tags-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.bulk-tag-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}
.tag-remove-btn {
  background: #fff0f0;
  color: #f56c6c;
  border: none;
}
.tag-add-btn {
  background: #f0f9eb;
  color: #67c23a;
  border: none;
}
.video-card {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 60%, #e0e7ef 100%);
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 8px;
  transition: box-shadow 0.2s;
}
.video-card:hover {
  box-shadow: 0 4px 16px #0002;
}
.video-icon {
  font-size: 64px;
  color: #409eff;
  filter: drop-shadow(0 2px 8px #409eff22);
  transition: color 0.2s, filter 0.2s;
}
.video-card:hover .video-icon {
  color: #1867c0;
  filter: drop-shadow(0 4px 16px #409eff44);
}
.tag-ellipsis {
  font-size: 18px;
  color: #909399;
  margin-left: 6px;
  font-weight: bold;
}
@media (max-width: 900px) {
  .search-container {
    padding: 4px;
  }
  .search-card {
    padding: 8px 2px;
  }
  .result-card, .result-media, .video-card {
    max-width: 100%;
  }
  .el-button, .el-input, .el-select, .el-form-item {
    font-size: 14px;
  }
}
@media (max-width: 600px) {
  .search-container {
    padding: 2px;
  }
  .search-card {
    padding: 2px 0;
  }
  .result-card, .result-media, .video-card {
    max-width: 100vw;
  }
  .el-button, .el-input, .el-select, .el-form-item {
    font-size: 12px;
  }
  .result-media {
    max-width: 100vw;
    height: auto;
  }
}

.audio-card {
  height: 200px;
  background: linear-gradient(135deg, #409EFF 0%, #36D1DC 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 4px;
  margin-bottom: 12px;
  position: relative;
}

.audio-card:hover {
  transform: scale(1.02);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.audio-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.audio-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
}

.audio-controls {
  position: absolute;
  bottom: 16px;
  display: flex;
  gap: 8px;
}

.audio-controls .el-button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  transition: all 0.3s ease;
}

.audio-controls .el-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .audio-card {
    height: 150px;
  }
  
  .audio-icon {
    font-size: 36px;
  }
  
  .audio-text {
    font-size: 14px;
    margin-bottom: 12px;
  }
  
  .audio-controls {
    bottom: 12px;
  }
}
</style> 