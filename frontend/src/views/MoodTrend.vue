<template>
  <div class="mood-trend">
    <el-card class="trend-card">
      <template #header>
        <div class="card-header">
          <h2>心情趋势</h2>
          <div class="time-selector">
            <el-select v-model="trendDays" @change="fetchTrendData">
              <el-option :value="7" label="最近7天" />
              <el-option :value="14" label="最近14天" />
              <el-option :value="30" label="最近30天" />
              <el-option :value="90" label="最近3个月" />
            </el-select>
          </div>
        </div>
      </template>

      <div class="chart-container" ref="trendChartRef" v-loading="loading" />
    </el-card>

    <!-- 情绪统计 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="stats-card">
          <template #header>
            <h3>情绪分布</h3>
          </template>
          <div class="pie-chart" ref="pieChartRef" v-loading="loading" />
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="stats-card">
          <template #header>
            <h3>时间段统计</h3>
          </template>
          <div class="time-stats">
            <el-form :inline="true" class="time-form">
              <el-form-item label="开始日期">
                <el-date-picker
                  v-model="timeRange.start"
                  type="date"
                  placeholder="选择日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
              <el-form-item label="结束日期">
                <el-date-picker
                  v-model="timeRange.end"
                  type="date"
                  placeholder="选择日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="fetchTimeStats">查询</el-button>
              </el-form-item>
            </el-form>

            <div class="stats-content" v-if="timeStats">
              <div class="stat-item">
                <span class="label">日记总数：</span>
                <span class="value">{{ timeStats.total_diaries }} 篇</span>
              </div>
              <div class="stat-item">
                <span class="label">平均情绪得分：</span>
                <span class="value">{{ timeStats.avg_emotion_score }}</span>
              </div>
              <div class="emotion-tags">
                <div
                  v-for="(count, tag) in timeStats.emotion_distribution"
                  :key="tag"
                  class="emotion-tag-item"
                >
                  <el-tag
                    :color="getMoodInfo(tag).color"
                    effect="dark"
                    size="small"
                  >
                    {{ getMoodInfo(tag).emoji }} {{ getMoodInfo(tag).label }}：{{ count }}篇
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'
import { getMoodInfo, moodTagMap } from '@/utils'

const loading = ref(false)
const trendDays = ref(30)
const trendData = ref([])
const emotionStats = ref(null)
const timeStats = ref(null)

const timeRange = reactive({
  start: '',
  end: ''
})

const trendChartRef = ref(null)
const pieChartRef = ref(null)

let trendChart = null
let pieChart = null

const fetchTrendData = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/stats/trend', {
      params: { days: trendDays.value }
    })
    if (res.data.code === 200) {
      trendData.value = res.data.data.trend
      renderTrendChart()
    }
  } catch (error) {
    console.error('获取趋势数据失败')
  } finally {
    loading.value = false
  }
}

const fetchEmotionStats = async () => {
  try {
    const res = await api.get('/api/stats/emotion')
    if (res.data.code === 200) {
      emotionStats.value = res.data.data
      renderPieChart()
    }
  } catch (error) {
    console.error('获取情绪统计失败')
  }
}

const fetchTimeStats = async () => {
  if (!timeRange.start || !timeRange.end) {
    return
  }
  try {
    const res = await api.get('/api/stats/time-range', {
      params: {
        start_date: timeRange.start,
        end_date: timeRange.end
      }
    })
    if (res.data.code === 200) {
      timeStats.value = res.data.data
    }
  } catch (error) {
    console.error('获取时间段统计失败')
  }
}

const renderTrendChart = () => {
  if (!trendChartRef.value) return

  if (trendChart) {
    trendChart.dispose()
  }

  trendChart = echarts.init(trendChartRef.value)

  const dates = trendData.value.map(d => d.date.slice(5)) // MM-DD
  const scores = trendData.value.map(d => d.avg_score)
  const counts = trendData.value.map(d => d.diary_count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['情绪得分', '日记数量']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: [
      {
        type: 'value',
        name: '情绪得分',
        min: 0,
        max: 1
      },
      {
        type: 'value',
        name: '日记数量',
        min: 0
      }
    ],
    series: [
      {
        name: '情绪得分',
        type: 'line',
        smooth: true,
        data: scores,
        itemStyle: {
          color: '#409EFF'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      },
      {
        name: '日记数量',
        type: 'bar',
        yAxisIndex: 1,
        data: counts,
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }

  trendChart.setOption(option)
}

const renderPieChart = () => {
  if (!pieChartRef.value || !emotionStats.value) return

  if (pieChart) {
    pieChart.dispose()
  }

  pieChart = echarts.init(pieChartRef.value)

  const data = emotionStats.value.emotions.map(e => ({
    name: e.emotion_name,
    value: e.count,
    itemStyle: { color: getMoodInfo(e.emotion_tag).color }
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}篇 ({d}%)'
    },
    series: [
      {
        name: '情绪分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data
      }
    ]
  }

  pieChart.setOption(option)
}

const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

onMounted(async () => {
  // 设置默认时间范围
  const today = new Date()
  const monthAgo = new Date()
  monthAgo.setMonth(monthAgo.getMonth() - 1)
  timeRange.start = monthAgo.toISOString().slice(0, 10)
  timeRange.end = today.toISOString().slice(0, 10)

  await nextTick()
  fetchTrendData()
  fetchEmotionStats()
  fetchTimeStats()

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.mood-trend {
  max-width: 1200px;
  margin: 0 auto;
}

.trend-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.chart-container {
  height: 400px;
}

.stats-card {
  margin-bottom: 20px;
}

.stats-card h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.pie-chart {
  height: 300px;
}

.time-form {
  margin-bottom: 20px;
}

.stats-content {
  padding: 16px 0;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.stat-item .label {
  color: #666;
}

.stat-item .value {
  font-weight: 500;
  color: #333;
}

.emotion-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.emotion-tag-item {
  display: flex;
}
</style>
