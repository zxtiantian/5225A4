<template>
  <div class="upload-container">
    <el-card class="upload-card">
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
            <h2>Upload Bird Media Files</h2>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="upload-tabs">
        <el-tab-pane label="Image Recognition" name="image">
          <el-upload
            ref="uploadRef"
            :file-list="fileList"
            class="upload-area"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleImageChange"
            :on-remove="handleFileRemove"
            :limit="1"
            accept="image/*"
          >
            <el-icon class="el-icon--upload"><picture-filled /></el-icon>
            <div class="el-upload__text">
              Drag image here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                Supports jpg, png formats, max file size 5MB
              </div>
            </template>
          </el-upload>
        </el-tab-pane>

        <el-tab-pane label="Video Recognition" name="video">
          <el-upload
            ref="uploadRef"
            :file-list="fileList"
            class="upload-area"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleVideoChange"
            :on-remove="handleFileRemove"
            :limit="1"
            accept="video/*"
          >
            <el-icon class="el-icon--upload"><video-camera-filled /></el-icon>
            <div class="el-upload__text">
              Drag video here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                Supports mp4, avi formats, max file size 50MB
              </div>
            </template>
          </el-upload>
        </el-tab-pane>

        <el-tab-pane label="Audio Recognition" name="audio">
          <el-upload
            ref="uploadRef"
            :file-list="fileList"
            class="upload-area"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleAudioChange"
            :on-remove="handleFileRemove"
            :limit="1"
            accept="audio/*"
          >
            <el-icon class="el-icon--upload"><headset /></el-icon>
            <div class="el-upload__text">
              Drag audio file here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                Supports wav, mp3 formats
              </div>
            </template>
          </el-upload>
        </el-tab-pane>
      </el-tabs>

      <!-- 预览区域 -->
      <div v-if="fileList.length > 0 && !uploading && !recognitionResult" class="preview-area">
        <!-- 图片预览 -->
        <template v-if="activeTab === 'image'">
          <el-image
            :src="previewUrl"
            fit="contain"
            class="preview-image"
          />
        </template>

        <!-- 视频预览 -->
        <template v-if="activeTab === 'video'">
          <video
            :src="previewUrl"
            controls
            class="preview-video"
          />
        </template>

        <!-- 音频预览 -->
        <template v-if="activeTab === 'audio'">
          <audio
            :src="previewUrl"
            controls
            class="preview-audio"
          />
        </template>

        <div class="preview-info">
          <p>Filename: {{ fileList[0].name }}</p>
          <p>Size: {{ formatFileSize(fileList[0].size) }}</p>
        </div>
      </div>

      <div class="upload-actions">
        <el-button
          type="primary"
          :loading="uploading"
          :disabled="fileList.length === 0"
          @click="handleUpload"
        >
          Start Recognition
        </el-button>
      </div>
    </el-card>

    <!-- 识别结果展示 -->
    <el-card v-if="recognitionResult || uploading" class="result-card">
      <template #header>
        <div class="card-header">
          <h3>Recognition Results</h3>
        </div>
      </template>

      <div class="result-content">
        <!-- 视频识别结果 -->
        <template v-if="activeTab === 'video'">
          <div v-if="!recognitionResult || recognitionResult.status === 'processing'" class="loading-state">
            <el-icon class="loading-icon"><Loading /></el-icon>
            <p>Video is being processed. Please wait...</p>
          </div>
          <div v-else-if="recognitionResult.status === 'completed'">
            <p>
              Video processing completed. 
              <span v-if="videoDownloadAvailable">
                <a href="javascript:void(0)" @click="downloadVideo" style="color:#409EFF;text-decoration:underline;cursor:pointer;margin-left:4px;">Download Video</a>
              </span>
            </p>
          </div>
          <el-descriptions :column="1" border v-if="recognitionResult && recognitionResult.detections">
            <el-descriptions-item label="Detected Birds">
              <div>
                <div v-for="(bird, index) in showAllVideoTags ? recognitionResult.detections : recognitionResult.detections.slice(0, 5)" :key="index">
                  <el-tag size="small" class="bird-tag">
                    {{ bird.name }} ({{ (bird.confidence * 100).toFixed(1) }}%)
                  </el-tag>
                  <span class="track-id">#{{ bird.trackId }}</span>
                </div>
                <div v-if="recognitionResult.detections && recognitionResult.detections.length > 5">
                  <el-button type="text" @click="showAllVideoTags = !showAllVideoTags" style="padding: 0; margin-top: 8px;">
                    {{ showAllVideoTags ? '收起' : '展开更多' }}
                  </el-button>
                </div>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="Recognition Time">
              {{ recognitionResult.timestamp }}
            </el-descriptions-item>
          </el-descriptions>
        </template>

        <!-- 图片识别结果 -->
        <template v-if="activeTab === 'image'">
          <div v-if="uploading && !recognitionResult" class="loading-state">
            <el-icon class="loading-icon"><Loading /></el-icon>
            <p>Image is being processed. Please wait...</p>
          </div>
          <template v-else>
            <div class="result-image-flex">
              <el-image
                v-if="resultImageUrl"
                :src="resultImageUrl"
                fit="contain"
                class="result-image"
              />
            </div>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="Detected Birds">
                <div v-for="(bird, index) in recognitionResult.detections" :key="index">
                  <el-tag size="small" class="bird-tag">
                    {{ bird.name }} ({{ (bird.confidence * 100).toFixed(1) }}%)
                  </el-tag>
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="Recognition Time">
                {{ recognitionResult.timestamp }}
              </el-descriptions-item>
            </el-descriptions>
          </template>
        </template>

        <!-- 音频识别结果 -->
        <template v-if="activeTab === 'audio'">
          <div v-if="uploading" class="loading-state">
            <el-icon class="loading-icon"><Loading /></el-icon>
            <p>Audio is being processed. Please wait...</p>
          </div>
          <template v-else-if="recognitionResult && recognitionResult.detections">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Detected Birds">
              <div v-for="(bird, index) in recognitionResult.detections" :key="index">
                <el-tag size="small" class="bird-tag">
                  {{ bird.name }} ({{ (bird.confidence * 100).toFixed(1) }}%)
                </el-tag>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="Recognition Time">
              {{ recognitionResult.timestamp }}
            </el-descriptions-item>
          </el-descriptions>
          </template>
        </template>
        <div v-if="recognitionResult" class="reupload-btn-bar">
          <el-button type="primary" plain @click="handleReupload">Upload New File</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  PictureFilled,
  VideoCameraFilled,
  Headset,
  ArrowLeft,
  Loading
} from '@element-plus/icons-vue'
import { uploadToS3, getStsCredentials } from '../utils/s3Upload'
import { Auth } from 'aws-amplify'
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'

const activeTab = ref('image')
const fileList = ref([])
const previewUrl = ref('')
const uploading = ref(false)
const recognitionResult = ref(null)
const showAllVideoTags = ref(false)
const pollingTimer = ref(null)
const pollingInterval = 5000 // 5秒
const API_BASE = 'https://olfkpkhzs7.execute-api.us-east-1.amazonaws.com'
const uploadRef = ref(null)

const handleImageChange = (file) => {
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('Image size cannot exceed 5MB')
    return
  }
  handleFileChange(file)
}

const handleVideoChange = (file) => {
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.error('Video size cannot exceed 50MB')
    return
  }
  handleFileChange(file)
}

const handleAudioChange = (file) => {
  handleFileChange(file)
}

const handleFileChange = (file) => {
  fileList.value = [file]
  previewUrl.value = URL.createObjectURL(file.raw)
  recognitionResult.value = null
}

const handleFileRemove = () => {
  fileList.value = []
  previewUrl.value = ''
  recognitionResult.value = null
}

const formatFileSize = (size) => {
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  } else {
    return (size / (1024 * 1024)).toFixed(2) + ' MB'
  }
}

const recognizeImage = async (s3Key) => {
  const res = await fetch('https://wm33a945l9.execute-api.us-east-1.amazonaws.com/recognize-image', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image_url: `s3://bird-recognition-files/${s3Key}`
    })
  });
  const data = await res.json();
  // 兼容直接返回 JSON 或 Proxy 格式
  if (data.annotatedImage || data.detections) {
    return data;
  }
  if (typeof data.body === 'string') {
    return JSON.parse(data.body);
  }
  return data.body;
}

// 视频识别API地址
const VIDEO_API_URL = 'https://qdeuqwo3li.execute-api.us-east-1.amazonaws.com/recognize-video';

// 视频识别结果视频URL
const resultVideoUrl = ref('');

// 上传视频后识别
async function recognizeVideo(s3Key) {
  const res = await fetch(VIDEO_API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_url: `s3://bird-recognition-files/${s3Key}`
    })
  });
  const data = await res.json();
  if (data.annotatedVideo || data.detections) {
    return data;
  }
  if (typeof data.body === 'string') {
    return JSON.parse(data.body);
  }
  return data.body;
}

// 获取S3视频Blob URL
async function getS3VideoUrl(s3url) {
  if (!s3url) return '';
  if (s3url.startsWith('s3://')) {
    const url = s3url.replace('s3://', '');
    const firstSlash = url.indexOf('/');
    const bucket = url.substring(0, firstSlash);
    const key = url.substring(firstSlash + 1);
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
    // 强制 mp4 用 video/mp4
    let mimeType = response.ContentType;
    if (!mimeType || mimeType === 'binary/octet-stream' || key.endsWith('.mp4')) {
      mimeType = 'video/mp4';
    }
    const blob = await streamToBlob(response.Body, mimeType);
    return URL.createObjectURL(blob);
  }
  return s3url;
}

// 监听视频识别结果，优先使用 annotatedVideoUrl
watch(() => recognitionResult.value, async (newVal) => {
  if (!newVal) {
    resultVideoUrl.value = '';
    return;
  }
  if (newVal.annotatedVideoUrl) {
    resultVideoUrl.value = newVal.annotatedVideoUrl;
  } else if (newVal.annotatedVideo) {
    resultVideoUrl.value = await getS3VideoUrl(newVal.annotatedVideo);
  } else {
    resultVideoUrl.value = '';
  }
});

// S3 路径转 HTTP URL
function s3ToHttpUrl(s3url) {
  if (!s3url) return '';
  if (s3url.startsWith('s3://')) {
    const url = s3url.replace('s3://', '');
    const firstSlash = url.indexOf('/');
    const bucket = url.substring(0, firstSlash);
    const key = url.substring(firstSlash + 1);
    return `https://${bucket}.s3.us-east-1.amazonaws.com/${key}`;
  }
  return s3url;
}

// 轮询查询识别结果
async function pollVideoResult(fileKey) {
  if (!fileKey) return
  try {
    const res = await fetch(`${API_BASE}/api/query_results?fileKey=${encodeURIComponent(fileKey)}`)
    const data = await res.json()
    if (data && data.status === 'done') {
      const result = data.result;
      result.status = 'completed'; // 标记已完成
      recognitionResult.value = result;
      clearInterval(pollingTimer.value)
      pollingTimer.value = null
    }
  } catch (e) {
    // 可选：处理异常
  }
}

// 音频识别API地址
const AUDIO_API_URL = 'https://rar6tgi2o0.execute-api.us-east-1.amazonaws.com/recognize-audio';

// 音频识别
async function recognizeAudio(s3Key) {
  try {
  const res = await fetch(AUDIO_API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      audio_url: `s3://bird-recognition-files/${s3Key}`
    })
  });
    
  if (!res.ok) {
      throw new Error('Recognition failed');
  }
    
    const data = await res.json();
  // 兼容直接返回 JSON 或 Proxy 格式
  if (data.detections) {
    return data;
  }
  if (typeof data.body === 'string') {
    return JSON.parse(data.body);
  }
  return data.body;
  } catch (error) {
    console.error('Audio recognition error:', error);
    throw new Error('Audio recognition failed: ' + error.message);
  }
}

const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('Please select a file to upload')
    return
  }

  try {
    await Auth.currentAuthenticatedUser();
  } catch (e) {
    ElMessage.error('You are not logged in, please login first.')
    return
  }

  uploading.value = true
  recognitionResult.value = null; // 确保开始新的识别时清除之前的结果
  
  try {
    const fileObj = fileList.value[0].raw;
    const file = fileObj instanceof Blob ? fileObj : new Blob([fileObj], { type: fileObj.type || 'application/octet-stream' });
    const key = `uploads/${fileObj.name || 'upload.bin'}`;
    await uploadToS3({ file, key });
    ElMessage.success('Upload successful! Recognizing...');
    
    if (activeTab.value === 'image') {
      const result = await recognizeImage(key);
      recognitionResult.value = result;
    } else if (activeTab.value === 'video') {
      await recognizeVideo(key);
      recognitionResult.value = { status: 'processing' };
      if (pollingTimer.value) clearInterval(pollingTimer.value)
      pollingTimer.value = setInterval(() => pollVideoResult(`results/${fileObj.name.replace(/\.[^.]+$/, '_detected.mp4')}`), pollingInterval)
    } else if (activeTab.value === 'audio') {
      const result = await recognizeAudio(key);
      if (result && result.detections) {
      recognitionResult.value = result;
      } else {
        throw new Error('No detection results received');
      }
    }
    
    fileList.value = [];
    previewUrl.value = '';
  } catch (error) {
    console.error('Upload error:', error);
    if (error.message && error.message.includes('No current user')) {
      ElMessage.error('Session expired, please login again.');
    } else {
      ElMessage.error(error.message || 'Upload failed, please try again later');
    }
    recognitionResult.value = null;
  } finally {
    uploading.value = false;
    if (uploadRef.value) uploadRef.value.clearFiles();
  }
}

async function streamToBlob(stream, mimeType) {
  const reader = stream.getReader();
  const chunks = [];
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  return new Blob(chunks, { type: mimeType });
}

async function getS3ImageUrl(s3url) {
  if (!s3url) return '';
  if (s3url.startsWith('s3://')) {
    const url = s3url.replace('s3://', '');
    const firstSlash = url.indexOf('/');
    const bucket = url.substring(0, firstSlash);
    const key = url.substring(firstSlash + 1);
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
    const blob = await streamToBlob(response.Body, response.ContentType || 'image/jpeg');
    return URL.createObjectURL(blob);
  }
  return s3url;
}

// 响应式变量用于存储 Blob URL
const resultImageUrl = ref('');

watch(() => recognitionResult.value?.annotatedImage, async (newVal) => {
  if (newVal) {
    resultImageUrl.value = await getS3ImageUrl(newVal);
  } else {
    resultImageUrl.value = '';
  }
});

watch(() => activeTab.value, (tab) => {
  if (tab === 'video') showAllVideoTags.value = false
  recognitionResult.value = null;
  fileList.value = [];
  previewUrl.value = '';
})

const videoDownloadAvailable = computed(() => {
  return recognitionResult.value && (recognitionResult.value.annotatedVideoUrl || recognitionResult.value.resultFile);
});

const downloadVideo = async () => {
  if (!recognitionResult.value) {
    ElMessage.error('No video available for download');
    return;
  }
  let s3url = recognitionResult.value.annotatedVideoUrl || recognitionResult.value.resultFile;
  if (!s3url) {
    ElMessage.error('No video available for download');
    return;
  }
  try {
    let bucket, key;
    if (s3url.startsWith('s3://')) {
      const url = s3url.replace('s3://', '');
      const firstSlash = url.indexOf('/');
      bucket = url.substring(0, firstSlash);
      key = url.substring(firstSlash + 1);
    } else if (s3url.startsWith('https://')) {
      const match = s3url.match(/^https:\/\/([^.]+)\.s3\.amazonaws\.com\/(.+)$/);
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
};

const handleReupload = () => {
  recognitionResult.value = null;
  fileList.value = [];
  previewUrl.value = '';
  if (uploadRef.value) uploadRef.value.clearFiles();
};
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.upload-card,
.result-card {
  margin-bottom: 20px;
}

.card-header {
  text-align: center;
}

.card-header h2,
.card-header h3 {
  margin: 0;
  color: #303133;
}

.upload-tabs {
  margin-bottom: 20px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
}

.preview-area {
  margin-top: 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  width: auto;
  height: auto;
  object-fit: contain;
  display: block;
  margin: 0 auto 10px auto;
  background: #f6f6f6;
  border-radius: 4px;
}

.full-image {
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
  display: block;
  margin: 0 auto;
  background: #f6f6f6;
}

.preview-video {
  width: 100%;
  max-height: 400px;
  margin-bottom: 20px;
  border-radius: 4px;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

.preview-audio {
  width: 100%;
  margin: 10px 0;
}

.preview-info {
  margin-top: 10px;
  color: #606266;
}

.preview-info p {
  margin: 5px 0;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.result-content {
  padding: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.result-image-flex {
  width: 100%;
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f6f6;
  border-radius: 4px;
  margin-bottom: 20px;
  overflow: hidden;
}

.result-image {
  height: 100%;
  width: auto;
  max-width: 100%;
  object-fit: contain;
  display: block;
  background: #f6f6f6;
}

.result-video {
  width: 100%;
  max-height: 400px;
  margin-bottom: 20px;
  border-radius: 4px;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

.bird-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.track-id,
.time-stamp {
  margin-left: 8px;
  color: #909399;
}

:deep(.el-descriptions__label) {
  width: 120px;
  font-weight: 500;
}

:deep(.el-tabs__nav) {
  width: 100%;
  display: flex;
}

:deep(.el-tabs__item) {
  flex: 1;
  text-align: center;
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

.loading-state {
  text-align: center;
  padding: 20px;
}

.loading-icon {
  margin-bottom: 10px;
}

.reupload-btn-bar {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  margin-bottom: 8px;
}

@media (max-width: 900px) {
  .upload-container {
    padding: 4px;
  }
  .upload-card, .result-card {
    padding: 8px 2px;
  }
  .upload-area, .preview-area, .result-image-flex, .result-video {
    max-width: 100%;
  }
  .el-button, .el-input, .el-select, .el-form-item {
    font-size: 14px;
  }
}
@media (max-width: 600px) {
  .upload-container {
    padding: 2px;
  }
  .upload-card, .result-card {
    padding: 2px 0;
  }
  .upload-area, .preview-area, .result-image-flex, .result-video {
    max-width: 100vw;
  }
  .el-button, .el-input, .el-select, .el-form-item {
    font-size: 12px;
  }
  .result-image, .preview-image {
    max-width: 100vw;
    height: auto;
  }
}
</style> 