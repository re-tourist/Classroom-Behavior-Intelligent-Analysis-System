<template>
  <el-card class="stats-card" shadow="hover">
    <div class="card-title">检测统计信息（文档核心指标）</div>
    <div class="stats-grid">
      <div class="stats-item">
        <div class="stats-label">总人数</div>
        <div class="stats-value">{{ detectStore.stats.total }}</div>
      </div>
      <div class="stats-item">
        <div class="stats-label">抬头人数</div>
        <div class="stats-value raise-color">{{ detectStore.stats.raiseHead }}</div>
      </div>
      <div class="stats-item">
        <div class="stats-label">低头人数</div>
        <div class="stats-value lower-color">{{ detectStore.stats.lowerHead }}</div>
      </div>
      <div class="stats-item">
        <div class="stats-label">抬头率</div>
        <div class="stats-value rate-color">
          {{ (detectStore.stats.raiseRate * 100).toFixed(2) }}%
          <el-progress
            :percentage="detectStore.stats.raiseRate * 100"
            size="small"
            class="rate-progress"
          ></el-progress>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { useDetectStore } from '@/stores/detectStore'
import { ElCard, ElProgress } from 'element-plus'

const detectStore = useDetectStore()
</script>

<style scoped lang="scss">
.stats-card {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.stats-item {
  padding: 15px;
  border-radius: 8px;
  background-color: #f9fafb;
}

.stats-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stats-value {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

/* 颜色区分 */
.raise-color {
  color: #10b981; /* 抬头-绿色 */
}

.lower-color {
  color: #ef4444; /* 低头-红色 */
}

.rate-color {
  color: #2563eb; /* 抬头率-蓝色 */
}

.rate-progress {
  margin-top: 8px;
  height: 6px;
}
</style>