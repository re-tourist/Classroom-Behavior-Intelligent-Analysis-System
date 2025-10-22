// Token存储键（本地存储）
const TOKEN_KEY = 'yolov5_head_detect_token'

// 设置Token
export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token)
}

// 获取Token
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY) || ''
}

// 移除Token
export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY)
}