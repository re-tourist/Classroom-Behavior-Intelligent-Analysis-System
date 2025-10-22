<template>
  <div class="chart-item">
    <h4 class="chart-title">抬头/低头人数对比</h4>
    <el-card class="chart-card">
      <echarts :option="peopleOption" class="chart" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import ECharts from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { ElCard } from 'element-plus'

use([BarChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent, CanvasRenderer])

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const peopleOption = ref({})

const initChart = () => {
  const frames = props.data.map(item => `帧${item.frame}`)
  
  peopleOption.value = {
    title: { text: '各帧抬头/低头人数对比' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['抬头人数', '低头人数'] },
    xAxis: { type: 'category', data: frames },
    yAxis: { type: 'value' },
    series: [
      {
        name: '抬头人数',
        type: 'bar',
        data: props.data.map(item => item.head_up),
        itemStyle: { color: '#10b981' }
      },
      {
        name: '低头人数',
        type: 'bar',
        data: props.data.map(item => item.head_down),
        itemStyle: { color: '#e53e3e' }
      }
    ]
  }
}

watch(() => props.data, initChart, { immediate: true })
</script>

<style scoped>
.chart-item {
  width: 100%;
}

.chart-title {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 15px;
  font-weight: 500;
  padding-left: 8px;
  border-left: 3px solid #4361ee;
}

.chart-card {
  border-radius: 6px;
  border: 1px solid #f0f2f5;
  box-shadow: none;
}

.chart {
  width: 100%;
  height: 400px;
}
</style>