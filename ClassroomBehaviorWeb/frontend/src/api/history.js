// src/api/history.js
import request from './request'

// 获取历史检测数据
export const getHistoryData = (params) => {
  return request({
    url: '/history/',
    method: 'get',
    params
  })
}
