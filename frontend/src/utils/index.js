import dayjs from 'dayjs'

// 情绪标签映射
export const moodTagMap = {
  happy: { label: '开心', color: '#67C23A', emoji: '😊' },
  sad: { label: '悲伤', color: '#909399', emoji: '😢' },
  neutral: { label: '平静', color: '#409EFF', emoji: '😌' },
  anxious: { label: '焦虑', color: '#E6A23C', emoji: '😰' },
  angry: { label: '愤怒', color: '#F56C6C', emoji: '😠' },
  peaceful: { label: '安宁', color: '#95D475', emoji: '☮️' },
  excited: { label: '兴奋', color: '#F89C28', emoji: '🎉' },
  grateful: { label: '感恩', color: '#EB9E34', emoji: '🙏' },
  tired: { label: '疲惫', color: '#A8A8A8', emoji: '😴' },
  confused: { label: '困惑', color: '#B37FEB', emoji: '😕' }
}

// 获取情绪标签信息
export function getMoodInfo(tag) {
  return moodTagMap[tag] || { label: '未知', color: '#909399', emoji: '❓' }
}

// 格式化日期
export function formatDate(date, format = 'YYYY-MM-DD') {
  return dayjs(date).format(format)
}

// 格式化日期时间
export function formatDateTime(datetime) {
  return dayjs(datetime).format('YYYY-MM-DD HH:mm:ss')
}

// 截断文本
export function truncateText(text, length = 100) {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}
