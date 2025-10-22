<template>
  <div class="chart-item">
    <h4 class="chart-title">抬头率趋势变化</h4>
    <el-card class="chart-card">
      <echarts :option="rateOption" class="chart" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import ECharts from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { ElCard } from 'element-plus'

use([LineChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent, CanvasRenderer])

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const rateOption = ref({})

const initChart = () => {
  const frames = props.data.map(item => `帧${item.frame}`)
  
  rateOption.value = {
    title: { text: '各帧抬头率变化趋势' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['实际抬头率', '平滑抬头率'] },
    xAxis: { type: 'category', data: frames },
    yAxis: { 
      type: 'value', 
      max: 100,
      axisLabel: { formatter: '{value}%' } 
    },
    series: [
      {
        name: '实际抬头率',
        type: 'line',
        data: props.data.map(item => (item.head_up_rate * 100).toFixed(2)),
        smooth: true,
        lineStyle: { color: '#10b981' }
      },
      {
        name: '平滑抬头率',
        type: 'line',
        data: props.data.map(item => (item.head_up_rate_smooth * 100).toFixed(2)),
        smooth: true,
        lineStyle: { color: '#4361ee' }
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