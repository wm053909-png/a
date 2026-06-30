<template>
  <div class="calendar-page">
    <el-card class="calendar-card">
      <template #header>
        <div class="card-header">
          <h2>日历视图</h2>
          <div class="month-selector">
            <el-button @click="prevMonth">
              <el-icon><ArrowLeft /></el-icon>
            </el-button>
            <span class="current-month">{{ currentYear }}年{{ currentMonth }}月</span>
            <el-button @click="nextMonth">
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </template>

      <div class="calendar-grid">
        <div class="weekday-header">
          <div v-for="day in weekDays" :key="day" class="weekday">{{ day }}</div>
        </div>

        <div class="days-grid">
          <div
            v-for="(day, index) in calendarDays"
            :key="index"
            class="day-cell"
            :class="{
              'other-month': !day.isCurrentMonth,
              'has-diary': day.diaryCount > 0,
              'is-today': day.isToday
            }"
            @click="handleDayClick(day)"
          >
            <span class="day-number">{{ day.date }}</span>
            <div class="diary-indicator" v-if="day.diaryCount > 0">
              <span class="count">{{ day.diaryCount }}</span>
              <div class="mood-dots" v-if="day.moodTags.length > 0">
                <span
                  v-for="(tag, i) in day.moodTags.slice(0, 3)"
                  :key="i"
                  class="mood-dot"
                  :style="{ backgroundColor: getMoodInfo(tag).color }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="legend">
        <span class="legend-title">心情图例：</span>
        <div class="legend-items">
          <div v-for="(info, tag) in moodTagMap" :key="tag" class="legend-item">
            <span class="dot" :style="{ backgroundColor: info.color }" />
            <span>{{ info.emoji }} {{ info.label }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 当天日记列表 -->
    <el-card v-if="selectedDate" class="selected-day-card">
      <template #header>
        <div class="card-header">
          <h3>{{ selectedDate }} 的日记</h3>
          <el-button type="primary" @click="goToNewDiary">
            <el-icon><Plus /></el-icon>
            写日记
          </el-button>
        </div>
      </template>

      <div v-if="selectedDayDiaries.length > 0" class="day-diaries">
        <div
          v-for="diary in selectedDayDiaries"
          :key="diary.id"
          class="day-diary-item"
          @click="viewDiary(diary.id)"
        >
          <div class="diary-header">
            <h4>{{ diary.title }}</h4>
            <el-tag
              :color="getMoodInfo(diary.mood_tag).color"
              effect="dark"
              size="small"
            >
              {{ getMoodInfo(diary.mood_tag).emoji }}
            </el-tag>
          </div>
          <p class="diary-preview">{{ diary.preview }}</p>
        </div>
      </div>
      <el-empty v-else description="当天暂无日记" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, ArrowRight, Plus } from '@element-plus/icons-vue'
import api from '@/api'
import { moodTagMap, getMoodInfo, truncateText } from '@/utils'

const router = useRouter()

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const selectedDate = ref(null)
const calendarData = ref([])
const selectedDayDiaries = ref([])

const weekDays = ['日', '一', '二', '三', '四', '五', '六']

const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value

  // 获取当月第一天是周几
  const firstDay = new Date(year, month - 1, 1).getDay()
  // 获取当月天数
  const daysInMonth = new Date(year, month, 0).getDate()
  // 获取上月天数
  const daysInPrevMonth = new Date(year, month - 1, 0).getDate()

  const days = []
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  // 上月日期
  for (let i = firstDay - 1; i >= 0; i--) {
    const date = daysInPrevMonth - i
    const monthStr = month === 1 ? 12 : month - 1
    const yearStr = month === 1 ? year - 1 : year
    const dateStr = `${yearStr}-${String(monthStr).padStart(2, '0')}-${String(date).padStart(2, '0')}`
    days.push({
      date,
      dateStr,
      isCurrentMonth: false,
      isToday: false,
      diaryCount: 0,
      moodTags: []
    })
  }

  // 当月日期
  for (let date = 1; date <= daysInMonth; date++) {
    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(date).padStart(2, '0')}`
    const dayData = calendarData.value.find(d => d.date === dateStr)
    days.push({
      date,
      dateStr,
      isCurrentMonth: true,
      isToday: dateStr === todayStr,
      diaryCount: dayData?.count || 0,
      moodTags: dayData?.mood_tags || []
    })
  }

  // 下月日期（补齐42天）
  const remaining = 42 - days.length
  for (let date = 1; date <= remaining; date++) {
    const monthStr = month === 12 ? 1 : month + 1
    const yearStr = month === 12 ? year + 1 : year
    const dateStr = `${yearStr}-${String(monthStr).padStart(2, '0')}-${String(date).padStart(2, '0')}`
    days.push({
      date,
      dateStr,
      isCurrentMonth: false,
      isToday: false,
      diaryCount: 0,
      moodTags: []
    })
  }

  return days
})

const fetchCalendarData = async () => {
  try {
    const res = await api.get('/api/stats/calendar', {
      params: {
        year: currentYear.value,
        month: currentMonth.value
      }
    })
    if (res.data.code === 200) {
      calendarData.value = res.data.data.days
    }
  } catch (error) {
    console.error('获取日历数据失败')
  }
}

const prevMonth = () => {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  fetchCalendarData()
}

const nextMonth = () => {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  fetchCalendarData()
}

const handleDayClick = async (day) => {
  if (!day.isCurrentMonth || day.diaryCount === 0) return

  selectedDate.value = day.dateStr
  try {
    const res = await api.get('/api/diaries', {
      params: {
        start_date: day.dateStr,
        end_date: day.dateStr,
        per_page: 100
      }
    })
    if (res.data.code === 200) {
      const diaries = res.data.data.items
      // 获取预览内容
      for (let diary of diaries) {
        try {
          const detailRes = await api.get(`/api/diaries/${diary.id}`)
          if (detailRes.data.code === 200) {
            diary.preview = truncateText(detailRes.data.data.content, 60)
          }
        } catch (e) {
          diary.preview = ''
        }
      }
      selectedDayDiaries.value = diaries
    }
  } catch (error) {
    console.error('获取日记列表失败')
  }
}

const goToNewDiary = () => {
  router.push({ path: '/diary/new', query: { date: selectedDate.value } })
}

const viewDiary = (id) => {
  router.push(`/diary/${id}`)
}

onMounted(() => {
  fetchCalendarData()
})
</script>

<style scoped>
.calendar-page {
  max-width: 1000px;
  margin: 0 auto;
}

.calendar-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2,
.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.month-selector {
  display: flex;
  align-items: center;
  gap: 16px;
}

.current-month {
  font-size: 16px;
  font-weight: 500;
  min-width: 100px;
  text-align: center;
}

.calendar-grid {
  margin-bottom: 20px;
}

.weekday-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f5f7fa;
  border-radius: 8px 8px 0 0;
}

.weekday {
  padding: 12px;
  text-align: center;
  font-weight: 500;
  color: #666;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #eee;
}

.day-cell {
  min-height: 80px;
  padding: 8px;
  background: white;
  cursor: pointer;
  transition: background 0.3s;
}

.day-cell:hover {
  background: #f5f7fa;
}

.day-cell.other-month {
  background: #fafafa;
}

.day-cell.other-month .day-number {
  color: #ccc;
}

.day-cell.is-today {
  background: #ecf5ff;
}

.day-cell.is-today .day-number {
  color: #409eff;
  font-weight: bold;
}

.day-cell.has-diary {
  background: #f0f9eb;
}

.day-number {
  font-size: 14px;
  color: #333;
}

.diary-indicator {
  margin-top: 4px;
}

.count {
  font-size: 12px;
  color: #67c23a;
  font-weight: 500;
}

.mood-dots {
  display: flex;
  gap: 3px;
  margin-top: 4px;
}

.mood-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.legend {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.legend-title {
  color: #666;
  font-size: 14px;
}

.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.legend-item .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.selected-day-card {
  margin-top: 20px;
}

.day-diaries {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.day-diary-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.day-diary-item:hover {
  background: #ecf5ff;
}

.diary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.diary-header h4 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.diary-preview {
  margin: 0;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}
</style>
