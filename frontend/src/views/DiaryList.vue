<template>
  <div class="diary-list">
    <!-- 搜索和筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索日记标题..."
        :prefix-icon="Search"
        clearable
        class="search-input"
      />
      <el-select v-model="filterMood" placeholder="筛选情绪" clearable class="mood-filter">
        <el-option
          v-for="(info, tag) in moodTagMap"
          :key="tag"
          :label="info.emoji + ' ' + info.label"
          :value="tag"
        />
      </el-select>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        class="date-filter"
      />
      <el-button type="primary" @click="fetchDiaries">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
    </div>

    <!-- 批量操作栏 -->
    <div class="batch-bar" v-if="selectedIds.length > 0">
      <span>已选择 {{ selectedIds.length }} 篇日记</span>
      <el-button type="danger" @click="handleBatchDelete">
        <el-icon><Delete /></el-icon>
        批量删除
      </el-button>
      <el-button @click="handleBatchExport">
        <el-icon><Download /></el-icon>
        批量导出
      </el-button>
      <el-dropdown @command="handleBatchMood">
        <el-button>
          <el-icon><PriceTag /></el-icon>
          批量修改情绪
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              v-for="(info, tag) in moodTagMap"
              :key="tag"
              :command="tag"
            >
              {{ info.emoji }} {{ info.label }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 日记列表 -->
    <div class="diary-cards" v-loading="loading">
      <el-empty v-if="diaries.length === 0 && !loading" description="还没有日记，快去写一篇吧！">
        <el-button type="primary" @click="router.push('/diary/new')">写日记</el-button>
      </el-empty>

      <div v-else class="cards-grid">
        <el-card
          v-for="diary in diaries"
          :key="diary.id"
          class="diary-card"
          shadow="hover"
        >
          <div class="card-header">
            <el-checkbox
              v-model="diary.selected"
              @change="handleSelect(diary)"
            />
            <span class="diary-date">{{ diary.diary_date }}</span>
            <el-tag
              :type="getMoodInfo(diary.mood_tag).type"
              :color="getMoodInfo(diary.mood_tag).color"
              effect="dark"
              size="small"
            >
              {{ getMoodInfo(diary.mood_tag).emoji }} {{ getMoodInfo(diary.mood_tag).label }}
            </el-tag>
          </div>

          <div class="card-body" @click="viewDiary(diary.id)">
            <h3 class="diary-title">{{ diary.title }}</h3>
            <div class="diary-preview" v-if="diary.preview">
              {{ diary.preview }}
            </div>
            <div class="ai-badge" v-if="diary.has_analysis">
              <el-tag type="success" size="small" effect="plain">
                <el-icon><MagicStick /></el-icon>
                AI已分析
              </el-tag>
            </div>
          </div>

          <div class="card-footer">
            <span class="create-time">{{ diary.created_at }}</span>
            <div class="actions">
              <el-button text type="primary" @click.stop="editDiary(diary.id)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button text type="danger" @click.stop="deleteDiary(diary.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchDiaries"
        @current-change="fetchDiaries"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Delete, Download, PriceTag, ArrowDown, Edit, MagicStick } from '@element-plus/icons-vue'
import api from '@/api'
import { moodTagMap, getMoodInfo, truncateText } from '@/utils'

const router = useRouter()

const loading = ref(false)
const diaries = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const filterMood = ref('')
const dateRange = ref([])
const selectedIds = ref([])

const fetchDiaries = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }

    if (filterMood.value) {
      params.mood_tag = filterMood.value
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const res = await api.get('/api/diaries', { params })
    if (res.data.code === 200) {
      const data = res.data.data
      diaries.value = data.items.map(item => ({
        ...item,
        preview: '',
        selected: false
      }))
      total.value = data.total

      // 获取每篇日记的预览内容
      for (let diary of diaries.value) {
        try {
          const detailRes = await api.get(`/api/diaries/${diary.id}`)
          if (detailRes.data.code === 200) {
            diary.preview = truncateText(detailRes.data.data.content, 80)
          }
        } catch (e) {
          // 忽略错误
        }
      }
    }
  } catch (error) {
    ElMessage.error('获取日记列表失败')
  } finally {
    loading.value = false
  }
}

const handleSelect = (diary) => {
  if (diary.selected) {
    selectedIds.value.push(diary.id)
  } else {
    selectedIds.value = selectedIds.value.filter(id => id !== diary.id)
  }
}

const viewDiary = (id) => {
  router.push(`/diary/${id}`)
}

const editDiary = (id) => {
  router.push(`/diary/${id}/edit`)
}

const deleteDiary = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这篇日记吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const res = await api.delete(`/api/diaries/${id}`)
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      fetchDiaries()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的${selectedIds.value.length}篇日记吗？`, '批量删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const res = await api.post('/api/diaries/batch', { ids: selectedIds.value })
    if (res.data.code === 200) {
      ElMessage.success(res.data.message)
      selectedIds.value = []
      fetchDiaries()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleBatchExport = async () => {
  try {
    const res = await api.post('/api/diaries/batch/export', {
      ids: selectedIds.value
    })
    if (res.data.code === 200) {
      // 下载JSON文件
      const data = res.data.data
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `日记导出_${new Date().toISOString().slice(0, 10)}.json`
      a.click()
      URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    }
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleBatchMood = async (moodTag) => {
  try {
    const res = await api.put('/api/diaries/batch/mood', {
      ids: selectedIds.value,
      mood_tag: moodTag
    })
    if (res.data.code === 200) {
      ElMessage.success(res.data.message)
      fetchDiaries()
    }
  } catch (error) {
    ElMessage.error('批量修改失败')
  }
}

// 搜索防抖
let searchTimer = null
watch(searchKeyword, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchDiaries()
  }, 300)
})

onMounted(() => {
  fetchDiaries()
})
</script>

<style scoped>
.diary-list {
  max-width: 1200px;
  margin: 0 auto;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-input {
  width: 250px;
}

.mood-filter {
  width: 150px;
}

.date-filter {
  width: 280px;
}

.batch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #ecf5ff;
  border-radius: 8px;
  margin-bottom: 20px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.diary-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.diary-card:hover {
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.diary-date {
  color: #666;
  font-size: 14px;
}

.card-body {
  min-height: 100px;
}

.diary-title {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.diary-preview {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.ai-badge {
  margin-top: 12px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.create-time {
  color: #999;
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 4px;
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
</style>
