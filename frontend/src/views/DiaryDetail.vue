<template>
  <div class="diary-detail" v-loading="loading">
    <el-card class="detail-card" v-if="diary">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h2>{{ diary.title }}</h2>
            <div class="meta">
              <span class="date">{{ diary.diary_date }}</span>
              <el-tag
                :color="getMoodInfo(diary.mood_tag).color"
                effect="dark"
                size="small"
              >
                {{ getMoodInfo(diary.mood_tag).emoji }} {{ getMoodInfo(diary.mood_tag).label }}
              </el-tag>
            </div>
          </div>
          <div class="header-right">
            <el-button @click="router.back()">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <el-button type="primary" @click="editDiary">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" @click="deleteDiary">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </template>

      <div class="diary-content">
        {{ diary.content }}
      </div>

      <div class="diary-footer">
        <span>创建时间：{{ diary.created_at }}</span>
        <span v-if="diary.updated_at !== diary.created_at">
          更新时间：{{ diary.updated_at }}
        </span>
      </div>
    </el-card>

    <!-- AI分析结果 -->
    <el-card v-if="diary?.analysis" class="analysis-card">
      <template #header>
        <div class="analysis-header">
          <el-icon><MagicStick /></el-icon>
          <span>AI情绪分析</span>
        </div>
      </template>

      <div class="analysis-content">
        <div class="emotion-result">
          <div class="emotion-item">
            <span class="label">情绪标签：</span>
            <el-tag
              :color="getMoodInfo(diary.analysis.emotion_label).color"
              effect="dark"
            >
              {{ getMoodInfo(diary.analysis.emotion_label).emoji }}
              {{ getMoodInfo(diary.analysis.emotion_label).label }}
            </el-tag>
          </div>
          <div class="emotion-item">
            <span class="label">情绪得分：</span>
            <el-progress
              :percentage="diary.analysis.emotion_score * 100"
              :color="getProgressColor(diary.analysis.emotion_score)"
              style="width: 200px"
            />
          </div>
        </div>

        <div class="ai-feedback">
          <h4>AI建议：</h4>
          <p>{{ diary.analysis.ai_feedback }}</p>
        </div>

        <div class="model-info">
          <small>分析模型：{{ diary.analysis.model_name }}</small>
          <small>分析时间：{{ diary.analysis.created_at }}</small>
        </div>
      </div>
    </el-card>

    <el-card v-else-if="diary && !loading" class="no-analysis">
      <el-empty description="暂无AI分析结果">
        <el-button type="primary" @click="triggerAnalysis">触发AI分析</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, Delete, MagicStick } from '@element-plus/icons-vue'
import api from '@/api'
import { getMoodInfo } from '@/utils'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const diary = ref(null)

const getProgressColor = (score) => {
  if (score >= 0.7) return '#67C23A'
  if (score >= 0.4) return '#409EFF'
  return '#F56C6C'
}

const fetchDiary = async () => {
  loading.value = true
  try {
    const res = await api.get(`/api/diaries/${route.params.id}`)
    if (res.data.code === 200) {
      diary.value = res.data.data
    } else {
      ElMessage.error('获取日记详情失败')
      router.back()
    }
  } catch (error) {
    ElMessage.error('获取日记详情失败')
    router.back()
  } finally {
    loading.value = false
  }
}

const editDiary = () => {
  router.push(`/diary/${route.params.id}/edit`)
}

const deleteDiary = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这篇日记吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const res = await api.delete(`/api/diaries/${route.params.id}`)
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      router.push('/diaries')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const triggerAnalysis = async () => {
  try {
    ElMessage.info('正在触发AI分析...')
    const res = await api.get(`/api/diaries/${route.params.id}/analysis`)
    if (res.data.code === 200) {
      diary.value.analysis = res.data.data
      ElMessage.success('AI分析完成')
    }
  } catch (error) {
    ElMessage.error('AI分析失败，请稍后再试')
  }
}

onMounted(() => {
  fetchDiary()
})
</script>

<style scoped>
.diary-detail {
  max-width: 800px;
  margin: 0 auto;
}

.detail-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #333;
}

.meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date {
  color: #666;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 8px;
}

.diary-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
  padding: 20px 0;
  border-bottom: 1px solid #eee;
}

.diary-footer {
  display: flex;
  gap: 20px;
  padding-top: 16px;
  color: #999;
  font-size: 13px;
}

.analysis-card {
  margin-top: 20px;
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
}

.analysis-content {
  padding: 10px 0;
}

.emotion-result {
  display: flex;
  gap: 40px;
  margin-bottom: 20px;
}

.emotion-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  color: #666;
  font-size: 14px;
}

.ai-feedback {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.ai-feedback h4 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 14px;
}

.ai-feedback p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}

.model-info {
  display: flex;
  justify-content: flex-end;
  gap: 20px;
  color: #999;
}

.no-analysis {
  margin-top: 20px;
}
</style>
