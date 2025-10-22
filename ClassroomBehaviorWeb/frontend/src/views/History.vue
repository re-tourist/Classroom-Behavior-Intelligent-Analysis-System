<template>
  <div class="history-container">
    <!-- 顶部导航栏 -->
    <HistoryNav />

    <main class="history-main">
      <el-card class="history-card" shadow="hover">
        <div class="card-header">
          <i class="el-icon-history card-icon"></i>
          <h3 class="card-title">历史检测数据统计</h3>
        </div>
        
        <!-- 筛选表单 -->
        <FilterForm 
          @filter="handleFilter" 
          @reset="resetFilter" 
        />
        
        <div class="chart-container">
          <!-- 抬头率趋势图 -->
          <RateChart :data="tableData" />
          
          <!-- 人数对比图 -->
          <PeopleChart :data="tableData" />
        </div>
        
        <!-- 数据表格 -->
        <DataTable :tableData="tableData" />
      </el-card>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElCard } from 'element-plus'
import { ElMessage } from 'element-plus'
import { getHistoryData } from '@/api/history'

import HistoryNav from '@/components/History/HistoryNav.vue'
import FilterForm from '@/components/History/FilterForm.vue'
import RateChart from '@/components/History/RateChart.vue'
import PeopleChart from '@/components/History/PeopleChart.vue'
import DataTable from '@/components/History/DataTable.vue'

const tableData = ref([])

const fetchHistoryData = async (params = {}) => {
  try {
    console.log('获取历史数据参数：', params)
    const res = await getHistoryData(params)
    if (res.data.code === 200) {
      tableData.value = res.data.data.columns.sort((a, b) => a.frame - b.frame)
    }
  } catch (err) {
    ElMessage.error('获取历史数据失败：' + (err.response?.data?.msg || err.message))
  }
}

const handleFilter = (params) => {
  fetchHistoryData(params)
}

const resetFilter = () => {
  fetchHistoryData()
}

onMounted(() => {
  fetchHistoryData()
})
</script>

<style scoped>
.history-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.history-main {
  padding: 20px;
}

.history-card {
  margin-bottom: 20px;
  border-radius: 6px;
  border: none;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f2f5;
}

.card-icon {
  font-size: 20px;
  color: #4361ee;
  margin-right: 10px;
}

.card-title {
  margin: 0;
  color: #333;
  font-size: 16px;
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin: 0 20px 30px;
}
</style>