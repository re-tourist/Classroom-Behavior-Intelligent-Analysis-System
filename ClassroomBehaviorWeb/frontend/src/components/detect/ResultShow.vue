<template>
  <el-card class="result-card" shadow="hover">
    <div class="card-title">检测结果展示</div>
    <div class="result-container">
      <!-- 无结果时显示提示 -->
      <div v-if="!detectStore.detectResult" class="empty-result">
        <el-empty
          description="请上传图片并点击「开始检测」"
          class="empty"
        ></el-empty>
      </div>

      <!-- 有结果时显示标注图 -->
      <div v-else class="has-result">
        <el-image
          :src="detectStore.detectResult"
          alt="检测标注图"
          class="annotated-img"
          fit="contain"
        ></el-image>
        <div class="result-note">
          <span class="label raise-label">● 抬头（raise_head）</span>
          <span class="label lower-label">● 低头（lower_head）</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { useDetectStore } from '@/stores/detectStore'
import { ElCard, ElImage, ElEmpty } from 'element-plus'

const detectStore = useDetectStore()
</script>

<style scoped lang="scss">
.result-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.result-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
}

.empty-result {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.has-result {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.annotated-img {
  width: 100%;
  max-height: 500px;
  border-radius: 4px;
}

.result-note {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #666;
}

.label {
  display: flex;
  align-items: center;
  gap: 5px;
}

.raise-label::before {
  content: '';
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #10b981; /* 抬头-绿色 */
}

.lower-label::before {
  content: '';
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #ef4444; /* 低头-红色 */
}
</style>