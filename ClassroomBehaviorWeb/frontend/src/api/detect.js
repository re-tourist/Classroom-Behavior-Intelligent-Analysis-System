import request from './request'

// 1. 上传图片接口
export const uploadImg = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/detect/upload',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 2. 图片推理接口（调用YOLO模型）
export const inferImg = (params) => {
  return request({
    url: '/detect/infer',
    method: 'post',
    data: params
  })
}

// 3. 获取标注图接口
export const getAnnotatedImg = (taskId) => {
  return request({
    url: `/detect/annotated-img`,
    method: 'get',
    params: { taskId }
  })
}
export const uploadVideo = (file) => {
  const formData = new FormData()
  formData.append('video', file)
  return request({
    url: '/detect/video/upload',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 新增：视频帧检测接口（支持进度回调）
export const inferVideoFrames = (params, onProgress) => {
  return request({
    url: '/detect/video/infer',
    method: 'post',
    data: params,
    onUploadProgress: (progressEvent) => {
      const percent = progressEvent.loaded / progressEvent.total
      onProgress?.(percent)
    }
  })
}

// 新增：获取视频帧标注图
export const getFrameAnnotatedImg = (frameId) => {
  return request({
    url: `/detect/video/frame-annotated`,
    method: 'get',
    params: { frameId }
  })
}