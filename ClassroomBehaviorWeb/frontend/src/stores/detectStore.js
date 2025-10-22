import { defineStore } from 'pinia'
import { uploadImg, inferImg, getAnnotatedImg } from '@/api/detect'
import { saveImg, exportStatsCSV } from '@/utils/file'

// 默认配置（从环境变量读取）
const DEFAULT_CONFIG = {
  confThreshold: parseFloat(import.meta.env.VITE_DEFAULT_CONF),
  iouThreshold: parseFloat(import.meta.env.VITE_DEFAULT_IOU),
  classes: import.meta.env.VITE_DETECT_CLASSES.split(',') // ['raise_head', 'lower_head']
}

export const useDetectStore = defineStore('detect', {
  state: () => ({
    config: { ...DEFAULT_CONFIG }, // 检测参数
    uploadImg: null, // 上传的原始图片（{name, url, type}）
    detectResult: null, // 检测结果（标注图URL）
    stats: { // 统计数据（文档核心需求）
      total: 0, // 总人数
      raiseHead: 0, // 抬头人数
      lowerHead: 0, // 低头人数
      raiseRate: 0.00 // 抬头率
    },
    loading: false, // 加载状态
    error: '' // 错误提示
  }),
  actions: {
    // 1. 上传图片（对接后端上传接口）
    async uploadImage(file) {
      this.loading = true
      this.error = ''
      try {
        const res = await uploadImg(file)
        this.uploadImg = {
          name: file.name,
          url: res.data.fileUrl,
          type: file.type
        }
        this.detectResult = null // 清空历史结果
        this.stats = { total: 0, raiseHead: 0, lowerHead: 0, raiseRate: 0.00 }
        return true
      } catch (err) {
        this.error = err.response?.data?.msg || '图片上传失败'
        return false
      } finally {
        this.loading = false
      }
    },
    // 2. 执行检测（调用YOLO模型推理）
    async runDetect() {
      if (!this.uploadImg) {
        this.error = '请先上传图片'
        return false
      }
      this.loading = true
      this.error = ''
      try {
        // 1. 调用推理接口，获取检测统计
        const inferRes = await inferImg({
          fileUrl: this.uploadImg.url,
          conf: this.config.confThreshold,
          iou: this.config.iouThreshold
        })
        // 更新统计数据
        this.stats = {
          total: inferRes.data.total,
          raiseHead: inferRes.data.raiseHead,
          lowerHead: inferRes.data.lowerHead,
          raiseRate: (inferRes.data.raiseHead / inferRes.data.total).toFixed(2) || 0
        }
        // 2. 获取标注图URL
        const annoRes = await getAnnotatedImg(inferRes.data.taskId)
        this.detectResult = annoRes.data.annotatedUrl
        return true
      } catch (err) {
        this.error = err.response?.data?.msg || '检测失败，请重试'
        return false
      } finally {
        this.loading = false
      }
    },
    // 3. 保存检测结果（图片）
    saveDetectResult() {
      if (!this.detectResult) {
        this.error = '无检测结果可保存'
        return false
      }
      saveImg(this.detectResult, `detect_result_${this.uploadImg.name}`)
      return true
    },
    // 4. 导出统计数据（CSV）
    exportStats() {
      if (this.stats.total === 0) {
        this.error = '无统计数据可导出'
        return false
      }
      const statsData = [
        {
          检测时间: new Date().toLocaleString(),
          原始图片名: this.uploadImg.name,
          总人数: this.stats.total,
          抬头人数: this.stats.raiseHead,
          低头人数: this.stats.lowerHead,
          抬头率: `${this.stats.raiseRate * 100}%`
        }
      ]
      exportStatsCSV(statsData, `stats_${new Date().getTime()}.csv`)
      return true
    },
    // 重置检测状态
    resetDetect() {
      this.uploadImg = null
      this.detectResult = null
      this.stats = { total: 0, raiseHead: 0, lowerHead: 0, raiseRate: 0.00 }
      this.error = ''
    }
  }
})