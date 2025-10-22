import { defineStore } from 'pinia'
import { login as apiLogin, register as apiRegister } from '@/api/auth'
import { setToken, removeToken } from '@/utils/auth'

// 过滤用户名特殊字符
const sanitizeUsername = (username) => {
  return username ? username.replace(/[^\u4e00-\u9fa5a-zA-Z0-9_]/g, '_') : ''
}

export const useUserStore = defineStore('user', {
  state: () => ({
    loading: false,
    error: '',
    isLoggedIn: !!localStorage.getItem('token'), // 现在使用token判断登录状态
    username: ''
  }),
  actions: {
    // 注册方法（对接后端API）
    async register(username, password) {
      this.loading = true
      this.error = ''
      try {
        if (!username || !password) {
          this.error = '用户名和密码不能为空'
          this.loading = false
          return false
        }
        
        const safeUsername = sanitizeUsername(username)
        const response = await apiRegister(safeUsername, password)
        
        if (response.data.status === 'success') {
          this.loading = false
          return true
        } else {
          this.error = response.data.message || '注册失败'
          this.loading = false
          return false
        }
      } catch (err) {
        this.error = err.response?.data?.message || '注册失败'
        this.loading = false
        return false
      }
    },

    // 登录方法（对接后端API）
    async login(username, password) {
      this.loading = true
      this.error = ''
      try {
        const safeUsername = sanitizeUsername(username)
        const response = await apiLogin(safeUsername, password)
        
        if (response.data.status === 'success') {
          // 登录成功：存储token和用户名
          setToken(response.data.token || 'auth_token') // 假设后端返回token
          this.username = safeUsername
          this.isLoggedIn = true
          this.loading = false
          return true
        } else {
          this.error = response.data.message || '登录失败'
          this.loading = false
          return false
        }
      } catch (err) {
        this.error = err.response?.data?.message || '用户名或密码错误'
        this.loading = false
        return false
      }
    },

    logout() {
      removeToken()
      this.isLoggedIn = false
      this.username = ''
    }
  }
})
