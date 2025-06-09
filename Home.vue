<template>
  <div class="home-container">
    <el-row :gutter="20" class="feature-row">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card recognition-card" @click="showSystemInfo">
          <el-icon class="feature-icon"><picture-filled /></el-icon>
          <h3>Bird Recognition</h3>
          <p>Advanced AI-powered bird recognition and classification system</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card" @click="$router.push('/search')">
          <el-icon class="feature-icon"><search /></el-icon>
          <h3>Search Birds</h3>
          <p>Search through our database of bird images and videos using tags</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card" @click="$router.push('/subscribe')">
          <el-icon class="feature-icon"><star /></el-icon>
          <h3>Subscription</h3>
          <p>Subscribe to bird species and get notifications for new detections</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="welcome-card">
      <template #header>
        <div class="welcome-header">
          <h2>Welcome to Bird Recognition System</h2>
        </div>
      </template>
      <div class="welcome-content">
        <p>
          Our system helps you identify and classify birds through advanced image
          recognition technology. Upload your bird photos, videos or audios, and our AI
          will help you identify the species and provide detailed information.
        </p>
        <p>
          Get started by uploading your media or searching through our extensive
          database of bird images and videos.
        </p>
      </div>
    </el-card>

    <el-card class="stats-card">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="8">
          <div class="stat-item">
            <h3>10,000+</h3>
            <p>Bird Species</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="8">
          <div class="stat-item">
            <h3>95%</h3>
            <p>Recognition Accuracy</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="8">
          <div class="stat-item">
            <h3>24/7</h3>
            <p>Available Service</p>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- System Information Dialog -->
    <el-dialog
      v-model="systemInfoVisible"
      title="Bird Recognition System Information"
      width="600px"
      class="system-info-dialog"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="System Version">
          v1.0.0
        </el-descriptions-item>
        <el-descriptions-item label="Recognition Models">
          <div class="model-info">
            <div class="model-item">
              <h4>Image Recognition</h4>
              <p>YOLO-based bird detection model</p>
              <ul>
                <li>Supports multiple bird species detection</li>
                <li>Real-time object tracking</li>
                <li>Confidence score for each detection</li>
              </ul>
            </div>
            <div class="model-item">
              <h4>Audio Recognition</h4>
              <p>BirdNET-based bird sound recognition</p>
              <ul>
                <li>Bird species identification from audio</li>
                <li>Timestamp-based detection</li>
                <li>Multiple species detection in single audio</li>
              </ul>
            </div>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Supported File Types">
          <div class="file-types">
            <div class="file-type-item">
              <el-tag type="success">Images</el-tag>
              <span>JPG, PNG (max 5MB)</span>
            </div>
            <div class="file-type-item">
              <el-tag type="warning">Videos</el-tag>
              <span>MP4, AVI (max 50MB)</span>
            </div>
            <div class="file-type-item">
              <el-tag type="info">Audio</el-tag>
              <span>WAV, MP3 (max 10MB)</span>
            </div>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="System Statistics">
          <div class="stats-grid">
            <div class="stat-box">
              <h4>10,000+</h4>
              <p>Bird Species</p>
            </div>
            <div class="stat-box">
              <h4>95%</h4>
              <p>Recognition Accuracy</p>
            </div>
            <div class="stat-box">
              <h4>24/7</h4>
              <p>Available Service</p>
            </div>
            <div class="stat-box">
              <h4>1,000+</h4>
              <p>Daily Recognitions</p>
            </div>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="systemInfoVisible = false">Close</el-button>
          <el-button type="primary" @click="goToUpload">
            Start Recognition
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Recognition Modes Dialog -->
    <el-dialog
      v-model="recognitionModesVisible"
      title="Choose Recognition Mode"
      width="500px"
      class="recognition-modes-dialog"
    >
      <div class="recognition-modes">
        <el-card 
          class="mode-card" 
          @click="startRecognition('image')"
          shadow="hover"
        >
          <el-icon class="mode-icon"><picture-filled /></el-icon>
          <div class="mode-content">
            <h4>Image Recognition</h4>
            <p>Upload bird photos for instant species identification</p>
            <ul>
              <li>Supports JPG, PNG formats</li>
              <li>Max file size: 5MB</li>
              <li>Multiple birds detection</li>
            </ul>
          </div>
        </el-card>

        <el-card 
          class="mode-card" 
          @click="startRecognition('video')"
          shadow="hover"
        >
          <el-icon class="mode-icon"><video-camera-filled /></el-icon>
          <div class="mode-content">
            <h4>Video Recognition</h4>
            <p>Analyze bird videos with real-time tracking</p>
            <ul>
              <li>Supports MP4, AVI formats</li>
              <li>Max file size: 50MB</li>
              <li>Bird movement tracking</li>
            </ul>
          </div>
        </el-card>

        <el-card 
          class="mode-card" 
          @click="startRecognition('audio')"
          shadow="hover"
        >
          <el-icon class="mode-icon"><headset /></el-icon>
          <div class="mode-content">
            <h4>Audio Recognition</h4>
            <p>Identify birds by their songs and calls</p>
            <ul>
              <li>Supports WAV, MP3 formats</li>
              <li>Max file size: 10MB</li>
              <li>Multiple species detection</li>
            </ul>
          </div>
        </el-card>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="recognitionModesVisible = false">Cancel</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Search, 
  PictureFilled,
  Clock,
  Star
} from '@element-plus/icons-vue'

const router = useRouter()
const systemInfoVisible = ref(false)
const recognitionModesVisible = ref(false)

const showSystemInfo = () => {
  systemInfoVisible.value = true
}

const goToUpload = () => {
  systemInfoVisible.value = false
  router.push('/upload')
}

const showRecognitionModes = () => {
  recognitionModesVisible.value = true
}

const startRecognition = (mode) => {
  recognitionModesVisible.value = false
  router.push({
    path: '/upload',
    query: { mode }
  })
}
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.feature-row {
  margin-bottom: 30px;
}

.feature-card {
  height: 100%;
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 20px;
}

.feature-card h3 {
  margin: 0 0 10px;
  color: #303133;
}

.feature-card p {
  margin: 0;
  color: #606266;
}

.welcome-card {
  margin-bottom: 30px;
}

.welcome-header {
  text-align: center;
}

.welcome-header h2 {
  margin: 0;
  color: #303133;
}

.welcome-content {
  text-align: center;
  color: #606266;
  line-height: 1.6;
}

.welcome-content p {
  margin: 0 0 15px;
}

.stats-card {
  text-align: center;
}

.stat-item {
  padding: 20px;
}

.stat-item h3 {
  margin: 0 0 10px;
  font-size: 36px;
  color: #409eff;
}

.stat-item p {
  margin: 0;
  color: #606266;
  font-size: 16px;
}

@media (max-width: 768px) {
  .feature-card {
    margin-bottom: 20px;
  }

  .stat-item {
    margin-bottom: 20px;
  }
}

.system-info-dialog :deep(.el-descriptions__label) {
  width: 150px;
  font-weight: 500;
}

.model-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.model-item h4 {
  margin: 0 0 10px;
  color: #303133;
}

.model-item p {
  margin: 0 0 10px;
  color: #606266;
}

.model-item ul {
  margin: 0;
  padding-left: 20px;
  color: #606266;
}

.model-item li {
  margin: 5px 0;
}

.file-types {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-type-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-type-item span {
  color: #606266;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stat-box {
  text-align: center;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stat-box h4 {
  margin: 0 0 5px;
  font-size: 24px;
  color: #409eff;
}

.stat-box p {
  margin: 0;
  color: #606266;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

.recognition-card {
  background: linear-gradient(135deg, #409eff 0%, #36cfc9 100%);
  color: white;
}

.recognition-card .feature-icon,
.recognition-card h3,
.recognition-card p {
  color: white;
}

.recognition-modes {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.mode-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.mode-card:hover {
  transform: translateY(-3px);
}

.mode-card .el-card__body {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 20px;
}

.mode-icon {
  font-size: 32px;
  color: #409eff;
  padding: 10px;
  background-color: #ecf5ff;
  border-radius: 8px;
}

.mode-content {
  flex: 1;
}

.mode-content h4 {
  margin: 0 0 8px;
  color: #303133;
  font-size: 18px;
}

.mode-content p {
  margin: 0 0 10px;
  color: #606266;
}

.mode-content ul {
  margin: 0;
  padding-left: 20px;
  color: #606266;
  font-size: 14px;
}

.mode-content li {
  margin: 4px 0;
}

@media (max-width: 768px) {
  .mode-card .el-card__body {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .mode-icon {
    margin-bottom: 10px;
  }

  .mode-content ul {
    text-align: left;
  }
}

@media (max-width: 900px) {
  .home-container {
    padding: 4px;
  }
  .feature-row, .welcome-card, .stats-card {
    padding: 8px 2px;
  }
  .feature-card, .stat-item {
    font-size: 14px;
    width: 100%;
  }
  .feature-icon {
    font-size: 32px;
  }
}
@media (max-width: 600px) {
  .home-container {
    padding: 2px;
  }
  .feature-row, .welcome-card, .stats-card {
    padding: 2px 0;
  }
  .feature-card, .stat-item {
    font-size: 12px;
    width: 100vw;
  }
  .feature-icon {
    font-size: 24px;
  }
  .welcome-header h2 {
    font-size: 18px;
  }
}
</style> 