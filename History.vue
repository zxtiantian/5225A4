<template>
  <div class="history-container">
    <el-card class="history-card">
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
            <h2>Recognition History</h2>
          </div>
        </div>
      </template>

      <div class="filter-section">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="Media Type">
            <el-select v-model="filterForm.mediaType" placeholder="All Types">
              <el-option label="All" value="all" />
              <el-option label="Image" value="image" />
              <el-option label="Video" value="video" />
              <el-option label="Audio" value="audio" />
            </el-select>
          </el-form-item>
          <el-form-item label="Date Range">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start date"
              end-placeholder="End date"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleFilter">
              <el-icon><Filter /></el-icon>
              Filter
            </el-button>
            <el-button @click="resetFilter">
              <el-icon><Refresh /></el-icon>
              Reset
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="historyList.length === 0" class="empty-result">
        <el-empty description="No recognition history found" />
      </div>

      <div v-else class="history-list">
        <el-timeline>
          <el-timeline-item
            v-for="item in historyList"
            :key="item.id"
            :timestamp="item.timestamp"
            :type="getTimelineItemType(item.mediaType)"
          >
            <el-card class="history-item">
              <div class="media-preview">
                <el-image
                  v-if="item.mediaType === 'image'"
                  :src="item.mediaUrl"
                  fit="cover"
                  class="preview-image"
                />
                <video
                  v-else-if="item.mediaType === 'video'"
                  :src="item.mediaUrl"
                  controls
                  class="preview-video"
                />
                <div v-else class="audio-preview">
                  <el-icon><Headset /></el-icon>
                  <audio :src="item.mediaUrl" controls></audio>
                </div>
              </div>
              
              <div class="recognition-info">
                <h3>Detected Birds:</h3>
                <div class="bird-tags">
                  <el-tag
                    v-for="(bird, index) in item.detections"
                    :key="index"
                    :type="getTagType(bird.confidence)"
                    class="bird-tag"
                  >
                    {{ bird.name }} ({{ (bird.confidence * 100).toFixed(1) }}%)
                  </el-tag>
                </div>
                <div class="item-actions">
                  <el-button
                    type="primary"
                    link
                    @click="viewDetails(item)"
                  >
                    View Details
                  </el-button>
                  <el-button
                    type="danger"
                    link
                    @click="deleteHistory(item.id)"
                  >
                    Delete
                  </el-button>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Filter, Refresh, Headset, ArrowLeft } from '@element-plus/icons-vue'

const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filterForm = reactive({
  mediaType: 'all',
  dateRange: []
})

// Mock data for demonstration
const historyList = ref([
  {
    id: 1,
    mediaType: 'image',
    mediaUrl: 'https://example.com/bird1.jpg',
    timestamp: '2024-03-15 14:30:00',
    detections: [
      { name: 'Sparrow', confidence: 0.958 },
      { name: 'Magpie', confidence: 0.892 }
    ]
  },
  {
    id: 2,
    mediaType: 'video',
    mediaUrl: 'https://example.com/bird2.mp4',
    timestamp: '2024-03-15 13:15:00',
    detections: [
      { name: 'Robin', confidence: 0.923 },
      { name: 'Blue Jay', confidence: 0.876 }
    ]
  },
  {
    id: 3,
    mediaType: 'audio',
    mediaUrl: 'https://example.com/bird3.mp3',
    timestamp: '2024-03-15 12:00:00',
    detections: [
      { name: 'Nightingale', confidence: 0.945 },
      { name: 'Canary', confidence: 0.812 }
    ]
  }
])

const getTimelineItemType = (mediaType) => {
  switch (mediaType) {
    case 'image':
      return 'primary'
    case 'video':
      return 'success'
    case 'audio':
      return 'warning'
    default:
      return 'info'
  }
}

const getTagType = (confidence) => {
  if (confidence >= 0.9) return 'success'
  if (confidence >= 0.7) return 'warning'
  return 'danger'
}

const handleFilter = () => {
  // Implement filter logic
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('Filter applied')
  }, 1000)
}

const resetFilter = () => {
  filterForm.mediaType = 'all'
  filterForm.dateRange = []
  handleFilter()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  // Implement pagination logic
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  // Implement pagination logic
}

const viewDetails = (item) => {
  // Implement view details logic
  ElMessage.info('View details: ' + item.id)
}

const deleteHistory = (id) => {
  ElMessageBox.confirm(
    'Are you sure you want to delete this record?',
    'Warning',
    {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning'
    }
  ).then(() => {
    // Implement delete logic
    ElMessage.success('Record deleted')
  }).catch(() => {
    ElMessage.info('Delete cancelled')
  })
}
</script>

<style scoped>
.history-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.history-card {
  margin-bottom: 20px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.history-list {
  margin-top: 20px;
}

.history-item {
  margin-bottom: 10px;
}

.media-preview {
  margin-bottom: 15px;
}

.preview-image {
  width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: 4px;
}

.preview-video {
  width: 100%;
  max-height: 200px;
  border-radius: 4px;
}

.audio-preview {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.audio-preview .el-icon {
  font-size: 24px;
  color: #409eff;
}

.recognition-info {
  margin-top: 10px;
}

.recognition-info h3 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #303133;
}

.bird-tags {
  margin: 10px 0;
}

.bird-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.item-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  text-align: center;
}

.empty-result {
  padding: 40px 0;
}

@media (max-width: 768px) {
  .filter-section :deep(.el-form-item) {
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

@media (max-width: 900px) {
  .history-container {
    padding: 8px;
  }
  .history-card {
    padding: 8px 2px;
  }
  .el-table, .el-card, .el-form, .el-button, .el-input, .el-form-item {
    font-size: 14px;
    max-width: 100%;
  }
}
@media (max-width: 600px) {
  .history-container {
    padding: 2px;
  }
  .history-card {
    padding: 2px 0;
  }
  .el-table, .el-card, .el-form, .el-button, .el-input, .el-form-item {
    font-size: 12px;
    max-width: 100vw;
  }
}
</style> 