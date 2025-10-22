<template>
  <div class="table-container">
    <el-card class="table-card">
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="frame" label="帧编号" align="center"></el-table-column>
        <el-table-column prop="persons" label="总人数" align="center"></el-table-column>
        <el-table-column prop="head_up" label="抬头人数" align="center"></el-table-column>
        <el-table-column prop="head_down" label="低头人数" align="center"></el-table-column>
        <el-table-column prop="head_up_rate" label="抬头率" align="center" :formatter="formatRate"></el-table-column>
        <el-table-column prop="head_up_rate_smooth" label="平滑抬头率" align="center" :formatter="formatRate"></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ElTable, ElTableColumn, ElCard } from 'element-plus'

const props = defineProps({
  tableData: {
    type: Array,
    default: () => []
  }
})

const formatRate = (row, column) => {
  return (row[column.property] * 100).toFixed(2) + '%'
}
</script>

<style scoped>
.table-container {
  margin: 0 20px 20px;
}

.table-card {
  border-radius: 6px;
  border: 1px solid #f0f2f5;
  box-shadow: none;
}

.el-table th {
  background-color: #f9fafb;
}

.el-table tr:hover > td {
  background-color: #f5f7ff !important;
}
</style>