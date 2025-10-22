import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import { useUserStore } from '@/stores/userStore'

// 创建Axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000, // 超时30秒（适配YOLO推理耗时）
  headers: { 'Content-Type': 'application/json' }
})

// 请求拦截器：添加Token
service.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (err) => Promise.reject(err)
)

// 响应拦截器：处理错误
service.interceptors.response.use(
  (res) => res, // 正常响应直接返回
  (err) => {
    const userStore = useUserStore()
    // Token失效（401）：跳转登录页
    if (err.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      userStore.logout()
      window.location.href = '/login'
    }
    // 其他错误提示
    ElMessage.error(err.response?.data?.msg || '请求失败，请重试')
    return Promise.reject(err)
  }
)

export default service