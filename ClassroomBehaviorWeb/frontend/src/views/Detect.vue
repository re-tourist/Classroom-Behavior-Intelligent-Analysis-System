<template>
  <div class="detect-container">
    <!-- 顶部导航栏：显示项目名+退出按钮 -->
    <header class="top-nav">
      <div class="nav-left">
        <i class="el-icon-camera nav-icon"></i>
        <h1 class="nav-title">YOLO课堂抬头检测系统</h1>
      </div>
      <el-button
        type="text"
        @click="handleLogout"
        class="logout-btn"
      >
        <i class="el-icon-logout"></i> 退出登录
      </el-button>
    </header>

    <main class="detect-main">
      <!-- 1. 功能控制区：上传+参数配置（卡片式布局） -->
      <div class="control-section">
        <!-- 1.1 上传检测文件卡片 -->
        <el-card class="control-card upload-card" shadow="hover">
          <div class="card-header">
            <i class="el-icon-upload card-icon"></i>
            <h3 class="card-title">上传检测文件</h3>
          </div>
          <div class="card-content">
            <!-- 文件类型切换 -->
            <div class="file-type-switch">
              <el-radio-group v-model="fileType" :disabled="isInferencing">
                <el-radio label="image">图片检测</el-radio>
                <el-radio label="video">视频帧检测</el-radio>
              </el-radio-group>
            </div>

            <el-upload
              class="uploader"
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :accept="fileType === 'image' ? imageTypes : videoTypes"
              drag
            >
              <i class="el-icon-video-camera upload-icon" v-if="fileType === 'video'"></i>
              <i class="el-icon-picture-outline upload-icon" v-else></i>
              <div class="upload-text">
                {{ fileType === 'video' ? '将视频拖拽到此处，或<em>点击上传</em>' : '将图片拖拽到此处，或<em>点击上传</em>' }}
              </div>
              <div class="upload-tip" slot="tip">
                {{ fileType === 'video' ? '支持格式：mp4、avi（单个文件不超过100MB）' : '支持格式：png/jpg/jpeg' }}
              </div>
            </el-upload>

            <!-- 已选文件预览 -->
            <div class="file-preview" v-if="selectedFile">
              <video 
                v-if="fileType === 'video' && imageUrl"
                :src="imageUrl"
                controls
                class="preview-video"
              ></video>
              <img
                v-else-if="fileType === 'image' && imageUrl"
                :src="imageUrl"
                :alt="selectedFile.name"
                class="preview-img"
              >
              <div class="file-info">
                <p class="file-name">{{ selectedFile.name }}</p>
                <p class="file-size">{{ (selectedFile.size / 1024 / 1024).toFixed(2) }} MB</p>
                <p class="file-duration" v-if="fileType === 'video'">{{ videoDuration }}s</p>
              </div>
              <el-button
                type="text"
                class="remove-file"
                @click="removeFile"
              >
                <i class="el-icon-close"></i> 移除
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 1.2 模型参数配置卡片 -->
        <el-card class="control-card param-card" shadow="hover">
          <div class="card-header">
            <i class="el-icon-sliders card-icon"></i>
            <h3 class="card-title">模型参数配置</h3>
          </div>
          <div class="card-content param-content">
            <!-- 置信度阈值 -->
            <div class="param-item">
              <label class="param-label">置信度阈值</label>
              <el-slider
                v-model="confidence"
                :min="0.2"
                :max="0.9"
                :step="0.05"
                :disabled="isInferencing"
                class="param-slider"
              />
              <span class="param-value">{{ confidence }}</span>
            </div>

            <!-- 帧检测间隔（仅视频模式显示） -->
            <div class="param-item" v-if="fileType === 'video'">
              <label class="param-label">帧检测间隔(s)</label>
              <el-slider
                v-model="frameInterval"
                :min="0.5"
                :max="5"
                :step="0.5"
                :disabled="isInferencing"
                class="param-slider"
              />
              <span class="param-value">{{ frameInterval }}</span>
            </div>

            <!-- 检测结果保存选项 -->
            <div class="param-item">
              <el-checkbox
                v-model="saveAnnotated"
                :disabled="isInferencing"
                class="save-checkbox"
              >
                <i class="el-icon-download"></i> 保存检测标注图
              </el-checkbox>
            </div>

            <!-- 功能按钮 -->
            <div class="param-btn-group">
              <el-button
                type="primary"
                @click="startInference"
                :disabled="!selectedFile || isInferencing"
                class="infer-btn"
              >
                <i class="el-icon-play"></i> 开始检测
              </el-button>
              <el-button
                type="warning"
                @click="stopInference"
                :disabled="!isInferencing"
                class="stop-btn"
              >
                <i class="el-icon-pause"></i> 停止
              </el-button>
              <!-- 新增历史数据按钮 -->
              <el-button
                type="info"
                @click="$router.push('/history')"
                :disabled="isInferencing"
                class="history-btn"
              >
                <i class="el-icon-history"></i> 历史数据
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 2. 检测结果区：标注图+统计数据（左右布局） -->
      <div class="result-section">
        <!-- 2.1 检测结果预览卡片 -->
        <el-card class="result-card preview-card" shadow="hover">
          <div class="card-header">
            <i class="el-icon-eye card-icon"></i>
            <h3 class="card-title">检测结果预览</h3>
          </div>
          <div class="card-content result-content">
            <!-- 无结果时提示 -->
            <div class="empty-result" v-if="!detectionResult">
              <i class="el-icon-placeholder empty-icon"></i>
              <p class="empty-text">上传文件并点击「开始检测」，结果将显示于此</p>
            </div>

            <!-- 有结果时显示标注图 -->
            <div class="annotated-result" v-else>
              <div class="img-wrapper" ref="imgWrapper">
                <img
                  :src="detectionResult.annotatedUrl"
                  alt="检测标注图"
                  class="annotated-img"
                >
              </div>

              <!-- 检测目标列表 -->
              <div class="detection-list">
                <h4 class="list-title">检测目标（共 {{ detectionResult.objects.length }} 个）</h4>
                <div class="list-items">
                  <div
                    class="list-item"
                    v-for="(obj, idx) in detectionResult.objects"
                    :key="idx"
                  >
                    <span class="item-class" :class="obj.class === 'raise_head' ? 'class-up' : 'class-down'">
                      {{ obj.class === 'raise_head' ? '抬头' : '低头' }}
                    </span>
                    <span class="item-conf">置信度：{{ obj.confidence.toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 2.2 统计数据卡片 -->
        <el-card class="result-card stat-card" shadow="hover">
          <div class="card-header">
            <i class="el-icon-chart card-icon"></i>
            <h3 class="card-title">检测数据统计</h3>
          </div>
          <div class="card-content stat-content">
            <!-- 无统计数据时提示 -->
            <div class="empty-stat" v-if="!detectionResult">
              <p class="empty-stat-text">检测完成后将显示统计数据</p>
            </div>

            <!-- 有统计数据时显示 -->
            <div class="stat-grid" v-else>
              <div class="stat-item">
                <span class="stat-label">总人数</span>
                <span class="stat-value">{{ totalPersons }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">抬头人数</span>
                <span class="stat-value stat-up">{{ headUpCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">低头人数</span>
                <span class="stat-value stat-down">{{ headDownCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">抬头率</span>
                <span class="stat-value stat-rate">{{ headUpRate.toFixed(2) }}</span>
              </div>
            </div>

            <!-- 抬头率进度条（可视化展示） -->
            <div class="rate-progress" v-if="detectionResult">
              <label class="progress-label">抬头率可视化</label>
              <el-progress
                :percentage="headUpRate * 100"
                :status="headUpRate > 0.8 ? 'success' : headUpRate > 0.5 ? 'normal' : 'warning'"
                class="progress-bar"
              />
            </div>

            <!-- 视频帧统计（仅视频模式显示） -->
            <div class="frame-list" v-if="fileType === 'video' && frameResults.length">
              <h4 class="list-title">视频帧检测结果（共 {{ totalFrames }} 帧）</h4>
              <el-scrollbar height="200px" class="frame-scroll">
                <div class="frame-items">
                  <div 
                    class="frame-item" 
                    v-for="(frame, idx) in frameResults" 
                    :key="idx"
                    @click="showFrameDetail(frame)"
                  >
                    <span class="frame-time">第 {{ frame.timestamp }}s</span>
                    <span class="frame-rate">抬头率: {{ frame.raiseRate.toFixed(2) }}</span>
                  </div>
                </div>
              </el-scrollbar>
            </div>
          </div>
        </el-card>
      </div>
    </main>

    <!-- 检测中弹窗 -->
    <el-dialog
      title="检测中"
      v-model="isInferencing"
      width="30%"
      :close-on-click-modal="false"
      :show-close="false"
    >
      <el-progress :percentage="inferenceProgress" status="success" class="infer-progress"></el-progress>
      <p class="infer-tip">
        {{ fileType === 'video' ? '正在处理视频帧，预计耗时较长...' : '正在处理图片，预计耗时1-3秒...' }}
      </p>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { ElMessage } from 'element-plus'
import { uploadImg, inferImg, getAnnotatedImg, uploadVideo, inferVideoFrames, getFrameAnnotatedImg } from '@/api/detect'

// 基础状态管理
const userStore = useUserStore()
const router = useRouter()
const imageTypes = 'image/png,image/jpeg,image/jpg'
const videoTypes = 'video/mp4,video/avi'

// 文件相关状态
const fileType = ref('image') // 'image' | 'video'
const selectedFile = ref(null)
const imageUrl = ref('')
const detectionResult = ref(null) // 检测结果：{ annotatedUrl, objects }

// 视频相关状态
const videoDuration = ref(0)
const frameInterval = ref(1)
const frameResults = ref([])
const totalFrames = ref(0)
const averageHeadUpRate = ref(0)

// 模型参数
const confidence = ref(0.45)
const saveAnnotated = ref(true)

// 推理状态
const isInferencing = ref(false)
const inferenceProgress = ref(0)
let progressInterval = null

// 统计数据
const totalPersons = ref(0)
const headUpCount = ref(0)
const headDownCount = ref(0)
const headUpRate = ref(0)

// 处理文件上传
const handleFileChange = (uploadFile) => {
  const file = uploadFile.raw
  if (!file) return
  selectedFile.value = file
  detectionResult.value = null
  frameResults.value = []
  totalFrames.value = 0
  averageHeadUpRate.value = 0

  if (file.type.startsWith('video/')) {
    const video = document.createElement('video')
    video.preload = 'metadata'
    video.onloadedmetadata = () => {
      videoDuration.value = Math.floor(video.duration)
      URL.revokeObjectURL(video.src)
    }
    video.src = URL.createObjectURL(file)
    imageUrl.value = URL.createObjectURL(file)
  } else {
    imageUrl.value = URL.createObjectURL(file)
  }
}

// 移除已选文件
const removeFile = () => {
  selectedFile.value = null
  imageUrl.value = ''
  detectionResult.value = null
  frameResults.value = []
  videoDuration.value = 0
  totalFrames.value = 0
}

// 开始检测
const startInference = async () => {
  if (!selectedFile.value) return

  isInferencing.value = true
  inferenceProgress.value = 0
  
  // 模拟进度更新
  progressInterval = setInterval(() => {
    if (inferenceProgress.value < 95) {
      inferenceProgress.value += Math.random() * 5
    }
  }, 500)

  try {
    if (fileType.value === 'image') {
      // 图片检测流程
      const uploadRes = await uploadImg(selectedFile.value, confidence.value)
      const inferRes = await inferImg(uploadRes.data.fileId, saveAnnotated.value)
      const annoRes = await getAnnotatedImg(inferRes.data.taskId)
      
      detectionResult.value = {
        annotatedUrl: annoRes.data.annotatedUrl,
        objects: inferRes.data.objects
      }
      
      // 更新统计数据
      headUpCount.value = inferRes.data.objects.filter(obj => obj.class === 'raise_head').length
      headDownCount.value = inferRes.data.objects.filter(obj => obj.class === 'lower_head').length
      totalPersons.value = headUpCount.value + headDownCount.value
      headUpRate.value = totalPersons.value > 0 ? headUpCount.value / totalPersons.value : 0
      
    } else {
      // 视频检测流程
      const uploadRes = await uploadVideo(selectedFile.value, confidence.value, frameInterval.value)
      const inferRes = await inferVideoFrames(uploadRes.data.fileId, saveAnnotated.value)
      
      // 保存所有帧结果
      frameResults.value = inferRes.data.frames
      totalFrames.value = inferRes.data.frames.length
      
      // 计算平均抬头率
      const totalRate = inferRes.data.frames.reduce((sum, frame) => sum + frame.raiseRate, 0)
      averageHeadUpRate.value = totalFrames.value > 0 ? (totalRate / totalFrames.value).toFixed(2) : 0
      
      // 显示第一帧结果
      if (frameResults.value.length > 0) {
        await showFrameDetail(frameResults.value[0])
      }
    }
    
    inferenceProgress.value = 100
    ElMessage.success(`${fileType.value === 'image' ? '图片' : '视频'}检测完成`)
  } catch (err) {
    ElMessage.error(`检测失败: ${err.response?.data?.message || err.message}`)
  } finally {
    clearInterval(progressInterval)
    progressInterval = null
    // 延迟关闭弹窗，让用户看到100%进度
    setTimeout(() => {
      isInferencing.value = false
      inferenceProgress.value = 0
    }, 500)
  }
}

// 停止检测
const stopInference = () => {
  // 实际项目中应该调用后端停止接口
  clearInterval(progressInterval)
  progressInterval = null
  isInferencing.value = false
  ElMessage.warning('已停止检测')
}

// 显示帧详情
const showFrameDetail = async (frame) => {
  const annoRes = await getFrameAnnotatedImg(frame.frameId)
  detectionResult.value = {
    annotatedUrl: annoRes.data.annotatedUrl,
    objects: frame.objects
  }
  
  // 更新统计数据
  headUpCount.value = frame.objects.filter(obj => obj.class === 'raise_head').length
  headDownCount.value = frame.objects.filter(obj => obj.class === 'lower_head').length
  totalPersons.value = headUpCount.value + headDownCount.value
  headUpRate.value = totalPersons.value > 0 ? headUpCount.value / totalPersons.value : 0
}

// 退出登录
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
  ElMessage.success('已退出登录')
}

// 组件卸载时清理
onUnmounted(() => {
  if (progressInterval) {
    clearInterval(progressInterval)
  }
})
</script>

<style scoped>
/* 主容器样式 */
.detect-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 顶部导航 */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.nav-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.nav-icon {
  font-size: 24px;
  color: #4361ee;
}
.nav-title {
  font-size: 18px;
  color: #2d3748;
  margin: 0;
}
.logout-btn {
  color: #718096;
  
  &:hover {
    color: #4361ee;
  }
}

/* 主内容区：间距+响应式布局 */
.detect-main {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

/* 功能控制区：上传+参数卡片横向排列 */
.control-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.control-card {
  flex: 1;
  min-width: 300px;
  border-radius: 12px;
  overflow: hidden;
  border: none;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s ease;

  &:hover {
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.08);
  }
}

/* 卡片通用样式：标题+内容间距 */
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
}
.card-icon {
  color: #4361ee;
  font-size: 18px;
}
.card-title {
  font-size: 16px;
  color: #2d3748;
  margin: 0;
  font-weight: 500;
}
.card-content {
  padding: 20px;
}

/* 上传卡片样式 */
.upload-card .card-content {
  padding: 20px;
}
.uploader {
  margin-bottom: 20px;
}
.upload-icon {
  font-size: 48px;
  color: #a0aec0;
}
.upload-text {
  color: #718096;
  margin-top: 10px;
}
.upload-text em {
  color: #4361ee;
  font-style: normal;
}
.upload-tip {
  color: #a0aec0;
  font-size: 12px;
}

/* 文件类型切换 */
.file-type-switch {
  margin-bottom: 15px;
  text-align: right;
}

/* 已选文件预览 */
.file-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 8px;
  position: relative;
}
.preview-img, .preview-video {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}
.file-info {
  flex: 1;
}
.file-name {
  font-size: 14px;
  color: #2d3748;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.file-size, .file-duration {
  font-size: 12px;
  color: #718096;
  margin: 0;
}
.remove-file {
  color: #e53e3e;
  position: absolute;
  right: 12px;
  top: 12px;

  &:hover {
    color: #c53030;
  }
}

/* 参数卡片样式 */
.param-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.param-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.param-label {
  width: 100px;
  font-size: 14px;
  color: #2d3748;
}
.param-slider {
  flex: 1;
}
.param-value {
  width: 50px;
  text-align: center;
  font-size: 14px;
  color: #4361ee;
  font-weight: 500;
}
.save-checkbox {
  color: #718096;
  font-size: 14px;

  & .el-checkbox__input.is-checked .el-checkbox__inner {
    background-color: #4361ee;
    border-color: #4361ee;
  }
}
.param-btn-group {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
.infer-btn {
  flex: 1;
  background-color: #4361ee;
  border-color: #4361ee;

  &:hover {
    background-color: #3a56d4;
    border-color: #3a56d4;
  }
}
.stop-btn {
  flex: 1;
  background-color: #ecc94b;
  border-color: #ecc94b;

  &:hover {
    background-color: #d69e2e;
    border-color: #d69e2e;
  }
}
/* 历史数据按钮样式 */
.history-btn {
  flex: 1;
  background-color: #3182ce;
  border-color: #3182ce;
  color: white;

  &:hover {
    background-color: #2b6cb0;
    border-color: #2b6cb0;
  }
}

/* 结果展示区 */
.result-section {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.result-card {
  flex: 1;
  min-width: 300px;
  border-radius: 12px;
  overflow: hidden;
  border: none;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

/* 结果预览卡片 */
.preview-card {
  min-width: 600px;
}
.result-content {
  min-height: 400px;
  display: flex;
  flex-direction: column;
}
.empty-result {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #a0aec0;
}
.empty-icon {
  font-size: 64px;
  margin-bottom: 15px;
}
.empty-text {
  font-size: 14px;
}
.annotated-result {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.img-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
  background-color: #f8fafc;
  border-radius: 8px;
}
.annotated-img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 4px;
}
.detection-list {
  padding: 10px 0;
}
.list-title {
  font-size: 14px;
  color: #2d3748;
  margin: 0 0 10px 0;
  font-weight: 500;
}
.list-items {
  max-height: 150px;
  overflow-y: auto;
}
.list-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #f8fafc;
  border-radius: 4px;
  margin-bottom: 8px;
}
.item-class {
  font-size: 14px;
  font-weight: 500;
}
.class-up {
  color: #10b981;
}
.class-down {
  color: #e53e3e;
}
.item-conf {
  font-size: 13px;
  color: #718096;
}

/* 统计数据卡片 */
.stat-card {
  max-width: 400px;
}
.stat-content {
  min-height: 400px;
  display: flex;
  flex-direction: column;
}
.empty-stat {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #a0aec0;
}
.empty-stat-text {
  font-size: 14px;
}
.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}
.stat-item {
  background-color: #f8fafc;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}
.stat-label {
  display: block;
  font-size: 14px;
  color: #718096;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
}
.stat-up {
  color: #10b981;
}
.stat-down {
  color: #e53e3e;
}
.stat-rate {
  color: #4361ee;
}
.rate-progress {
  padding: 10px 0;
}
.progress-label {
  display: block;
  font-size: 14px;
  color: #718096;
  margin-bottom: 8px;
}
.progress-bar {
  width: 100%;
}

/* 视频帧列表 */
.frame-list {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px dashed #e2e8f0;
}
.frame-scroll {
  width: 100%;
}
.frame-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.frame-item {
  padding: 10px 15px;
  background-color: #f8fafc;
  border-radius: 6px;
  font-size: 14px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  justify-content: space-between;
  
  &:hover {
    background-color: #edf2f7;
  }
}
.frame-time {
  font-weight: 500;
}
.frame-rate {
  color: #4361ee;
}

/* 检测中弹窗 */
.infer-progress {
  margin-bottom: 15px;
}
.infer-tip {
  text-align: center;
  color: #718096;
  margin: 0;
}
</style>
