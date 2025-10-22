<template>
  <el-card class="upload-card" shadow="hover">
    <div class="card-title">图片上传（支持JPG/PNG）</div>
    <el-upload
      class="upload-area"
      :drag="true"
      :auto-upload="true"
      :file-list="fileList"
      :before-upload="beforeUpload"
      :on-success="onSuccess"
      :on-error="onError"
      :on-remove="onRemove"
      action="#"
      :limit="1"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">
        将图片拖拽到此处，或<em>点击上传</em>
      </div>
      <div class="el-upload__tip" slot="tip">
        支持格式：JPG、PNG（单个文件不超过10MB）
      </div>
    </el-upload>

    <!-- 上传预览 -->
    <div v-if="detectStore.uploadImg" class="img-preview">
      <div class="preview-title">上传预览</div>
      <el-image
        :src="detectStore.uploadImg.url"
        alt="上传预览图"
        class="preview-img"
        fit="contain"
      ></el-image>
      <div class="img-name">{{ detectStore.uploadImg.name }}</div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useDetectStore } from '@/stores/detectStore'
import { ElCard, ElUpload, ElImage, ElMessage, ElIcon } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'

const detectStore = useDetectStore()
const fileList = ref([])

// 监听上传图片变化，同步文件列表
watch(
  () => detectStore.uploadImg,
  (newVal) => {
    fileList.value = newVal ? [{ name: newVal.name, url: newVal.url }] : []
  },
  { immediate: true }
)

// 上传前验证
const beforeUpload = (file) => {
  // 验证格式
  const isImg = file.type === 'image/jpeg' || file.type === 'image/png'
  if (!isImg) {
    ElMessage.error('仅支持JPG、PNG格式图片')
    return false
  }
  // 验证大小（10MB）
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过10MB')
    return false
  }
  return true
}

// 上传成功
const onSuccess = async (response, file) => {
  const success = await detectStore.uploadImage(file)
  if (success) {
    ElMessage.success(`图片 "${file.name}" 上传成功`)
  }
}

// 上传失败
const onError = (err, file) => {
  ElMessage.error(`图片 "${file.name}" 上传失败: ${err.message}`)
}

// 移除图片
const onRemove = () => {
  detectStore.resetDetect()
  ElMessage.info('已移除上传图片')
}
</script>

<style scoped lang="scss">
.upload-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.upload-area {
  margin-bottom: 20px;
}

.img-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 15px;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
}

.preview-title {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.preview-img {
  width: 100%;
  height: 200px;
  border-radius: 4px;
}

.img-name {
  font-size: 12px;
  color: #999;
}
</style>