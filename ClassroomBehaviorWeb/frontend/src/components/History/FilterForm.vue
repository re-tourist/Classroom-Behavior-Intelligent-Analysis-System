<template>
  <div class="filter-form">
    <!-- 表单标题栏 -->
    <div class="filter-header">
      <div class="filter-header-left">
        <div class="filter-icon">
          <i class="el-icon-filter"></i>
        </div>
        <div class="filter-header-text">
          <h4 class="filter-title">数据筛选</h4>
          <p class="filter-subtitle">设置筛选条件，精确查找历史记录</p>
        </div>
      </div>
      <div class="filter-divider"></div>
    </div>
    
    <!-- 表单内容区 -->
    <el-form :inline="true" :model="filterForm" class="filter-form-inner">
      <!-- 第一行筛选项 -->
      <div class="filter-row">
        <el-form-item label="帧编号" class="filter-item">
          <el-input 
            v-model="filterForm.frame" 
            placeholder="请输入帧编号"
            class="filter-input"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="总人数范围" class="filter-item">
          <div class="range-group">
            <el-input-number 
              v-model="filterForm.min_persons" 
              placeholder="最小值" 
              :min="0" 
              size="small"
              class="range-input"
            ></el-input-number>
            <span class="range-separator">至</span>
            <el-input-number 
              v-model="filterForm.max_persons" 
              placeholder="最大值" 
              :min="0" 
              size="small"
              class="range-input"
            ></el-input-number>
          </div>
        </el-form-item>
        
        <el-form-item label="抬头率范围(%)" class="filter-item">
          <div class="range-group">
            <el-input-number 
              v-model="filterForm.min_rate" 
              placeholder="最小值" 
              :min="0" 
              :max="100" 
              size="small"
              class="range-input"
            ></el-input-number>
            <span class="range-separator">至</span>
            <el-input-number 
              v-model="filterForm.max_rate" 
              placeholder="最大值" 
              :min="0" 
              :max="100" 
              size="small"
              class="range-input"
            ></el-input-number>
          </div>
        </el-form-item>
      </div>
      
      <!-- 第二行筛选项 -->
      <div class="filter-row">
        <el-form-item label="抬头人数范围" class="filter-item">
          <div class="range-group">
            <el-input-number 
              v-model="filterForm.min_head_up" 
              placeholder="最小值" 
              :min="0" 
              size="small"
              class="range-input"
            ></el-input-number>
            <span class="range-separator">至</span>
            <el-input-number 
              v-model="filterForm.max_head_up" 
              placeholder="最大值" 
              :min="0" 
              size="small"
              class="range-input"
            ></el-input-number>
          </div>
        </el-form-item>
        
        <el-form-item label="低头人数范围" class="filter-item">
          <div class="range-group">
            <el-input-number 
              v-model="filterForm.min_head_down" 
              placeholder="最小值" 
              :min="0" 
              size="small"
              class="range-input"
            ></el-input-number>
            <span class="range-separator">至</span>
            <el-input-number 
              v-model="filterForm.max_head_down" 
              placeholder="最大值" 
              :min="0" 
              size="small"
              class="range-input"
            ></el-input-number>
          </div>
        </el-form-item>
        
        <el-form-item label="平滑率范围(%)" class="filter-item">
          <div class="range-group">
            <el-input-number 
              v-model="filterForm.min_rate_smooth" 
              placeholder="最小值" 
              :min="0" 
              :max="100" 
              size="small"
              class="range-input"
            ></el-input-number>
            <span class="range-separator">至</span>
            <el-input-number 
              v-model="filterForm.max_rate_smooth" 
              placeholder="最大值" 
              :min="0" 
              :max="100" 
              size="small"
              class="range-input"
            ></el-input-number>
          </div>
        </el-form-item>
        
        <!-- 操作按钮 -->
        <el-form-item class="filter-actions">
          <div class="btn-group">
            <el-button 
              type="primary" 
              @click="handleFilter"
              class="filter-btn"
            >
              <i class="el-icon-search"></i> 查询
            </el-button>
            <el-button 
              @click="resetFilter"
              class="reset-btn"
            >
              <i class="el-icon-refresh"></i> 重置
            </el-button>
          </div>
        </el-form-item>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElForm, ElFormItem, ElInput, ElInputNumber, ElButton } from 'element-plus'

const filterForm = ref({
  frame: '',
  min_persons: null,
  max_persons: null,
  min_rate: null,
  max_rate: null,
  min_head_up: null,
  max_head_up: null,
  min_head_down: null,
  max_head_down: null,
  min_rate_smooth: null,
  max_rate_smooth: null
})

const emit = defineEmits(['filter', 'reset'])

const handleFilter = () => {
  const params = {}
  Object.keys(filterForm.value).forEach(key => {
    const value = filterForm.value[key]
    if (value !== null && value !== '' && value !== undefined) {
      if (key === 'min_rate' || key === 'max_rate' || key === 'min_rate_smooth' || key === 'max_rate_smooth') {
        params[key] = (value / 100).toString()
      } else {
        params[key] = value.toString()
      }
    }
  })
  emit('filter', params)
}

const resetFilter = () => {
  Object.keys(filterForm.value).forEach(key => {
    filterForm.value[key] = key.includes('min_') || key.includes('max_') ? null : ''
  })
  emit('reset')
}
</script>

<style scoped>
.filter-form {
  margin: 0 20px 25px;
  padding: 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: 1px solid #f0f2f5;
}

/* 表单头部 */
.filter-header {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background-color: #f9fafb;
  border-bottom: 1px solid #f0f2f5;
}

.filter-header-left {
  display: flex;
  align-items: center;
}

.filter-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: rgba(67, 97, 238, 0.1);
  color: #4361ee;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.filter-title {
  margin: 0 0 3px 0;
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.filter-subtitle {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.filter-divider {
  flex: 1;
}

/* 表单内容区 */
.filter-form-inner {
  padding: 20px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px 25px;
  margin-bottom: 15px;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-item {
  display: flex;
  align-items: center;
  margin-bottom: 0 !important;
}

.el-form-item__label {
  width: 100px;
  color: #606266;
  font-size: 14px;
  padding-right: 12px;
  line-height: 1;
  white-space: nowrap;
}

/* 输入框美化 */
.filter-input {
  width: 180px;
  height: 34px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  transition: all 0.2s ease;
}

.filter-input:focus {
  border-color: #4361ee;
  box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.2);
  outline: none;
}

/* 范围选择组 */
.range-group {
  display: flex;
  align-items: center;
}

.range-input {
  width: 120px;
  height: 34px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  transition: all 0.2s ease;
}

.range-input:focus {
  border-color: #4361ee;
  box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.2);
}

.range-separator {
  margin: 0 10px;
  color: #c0c4cc;
  font-size: 14px;
}

/* 按钮区域 */
.filter-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.btn-group {
  display: flex;
  gap: 12px;
}

.filter-btn {
  background-color: #4361ee;
  border-color: #4361ee;
  padding: 8px 20px;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  background-color: #3a56d4;
  border-color: #3a56d4;
  transform: translateY(-1px);
}

.filter-btn:active {
  transform: translateY(0);
}

.reset-btn {
  background-color: #f5f7fa;
  color: #606266;
  border-color: #dcdfe6;
  padding: 8px 20px;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.reset-btn:hover {
  background-color: #e9ecef;
  border-color: #c9cdcf;
  transform: translateY(-1px);
}

.reset-btn:active {
  transform: translateY(0);
}
</style>