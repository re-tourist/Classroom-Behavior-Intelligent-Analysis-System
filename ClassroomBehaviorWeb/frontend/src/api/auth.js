import request from './request'

// 登录接口（对接后端）
export const login = (username, password) => {
  return request({
    url: '/login/',
    method: 'post',
    // 注意：后端使用的是form-data格式，而非之前的json
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    data: new URLSearchParams({ username, password })
  })
}

// 注册接口（对接后端）
export const register = (username, password) => {
  return request({
    url: '/register/',
    method: 'post',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    data: new URLSearchParams({ username, password })
  })
}

// 获取用户信息接口
export const getUserInfo = () => {
  return request({
    url: '/info/',
    method: 'get'
  })
}
