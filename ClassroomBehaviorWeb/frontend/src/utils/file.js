import Papa from 'papaparse'

// 1. 保存图片（检测结果）
export const saveImg = (imgUrl, filename) => {
  const link = document.createElement('a')
  link.href = imgUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 2. 导出统计数据为CSV（文档需求：保存结果）
export const exportStatsCSV = (data, filename) => {
  const csv = Papa.unparse(data)
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}