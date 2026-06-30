<template>
  <div class="diary-edit">
    <el-card class="edit-card">
      <template #header>
        <div class="card-header">
          <h2>{{ isEdit ? '编辑日记' : '写日记' }}</h2>
          <el-button @click="router.back()">返回</el-button>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="日期" prop="diary_date">
          <el-date-picker
            v-model="form.diary_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="给今天的日记起个标题"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="心情" prop="mood_tag">
          <el-select v-model="form.mood_tag" placeholder="选择今天的心情">
            <el-option
              v-for="(info, tag) in moodTagMap"
              :key="tag"
              :label="info.emoji + ' ' + info.label"
              :value="tag"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            placeholder="写下你今天的心情和故事..."
            :rows="12"
            maxlength="5000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">
            {{ saving ? '保存中...' : '保存日记' }}
          </el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- AI分析结果展示 -->
    <el-card v-if="analysisResult" class="analysis-card">
      <template #header>
        <div class="analysis-header">
          <el-icon><MagicStick /></el-icon>
          <span>AI情绪分析结果</span>
        </div>
      </template>

      <div class="analysis-content">
        <div class="emotion-result">
          <div class="emotion-label">
            <span class="label">情绪标签：</span>
            <el-tag
              :color="getMoodInfo(analysisResult.emotion_label).color"
              effect="dark"
            >
              {{ getMoodInfo(analysisResult.emotion_label).emoji }}
              {{ getMoodInfo(analysisResult.emotion_label).label }}
            </el-tag>
          </div>
          <div class="emotion-score">
            <span class="label">情绪得分：</span>
            <el-progress
              :percentage="analysisResult.emotion_score * 100"
              :color="getProgressColor(analysisResult.emotion_score)"
            />
          </div>
        </div>

        <div class="ai-feedback">
          <h4>AI建议：</h4>
          <p>{{ analysisResult.ai_feedback }}</p>
        </div>

        <div class="model-info">
          <small>分析模型：{{ analysisResult.model_name }}</small>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import api from '@/api'
import { moodTagMap, getMoodInfo } from '@/utils'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const formRef = ref(null)
const saving = ref(false)
const analysisResult = ref(null)

const form = reactive({
  title: '',
  content: '',
  diary_date: dayjs().format('YYYY-MM-DD'),
  mood_tag: 'neutral'
})

const rules = {
  title: [
    { required: true, message: '请输入日记标题', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入日记内容', trigger: 'blur' }
  ],
  diary_date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ]
}

const getProgressColor = (score) => {
  if (score >= 0.7) return '#67C23A'
  if (score >= 0.4) return '#409EFF'
  return '#F56C6C'
}

const fetchDiary = async () => {
  if (!isEdit.value) return

  try {
    const res = await api.get(`/api/diaries/${route.params.id}`)
    if (res.data.code === 200) {
      const diary = res.data.data
      form.title = diary.title
      form.content = diary.content
      form.diary_date = diary.diary_date
      form.mood_tag = diary.mood_tag

      // 获取AI分析结果
      if (diary.analysis) {
        analysisResult.value = diary.analysis
      }
    }
  } catch (error) {
    ElMessage.error('获取日记详情失败')
    router.back()
  }
}

const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    let res
    if (isEdit.value) {
      res = await api.put(`/api/diaries/${route.params.id}`, form)
    } else {
      res = await api.post('/api/diaries', form)
    }

    if (res.data.code === 200) {
      ElMessage.success(isEdit.value ? '修改成功' : '日记保存成功')

      // 如果是新建日记，展示AI分析结果
      if (!isEdit.value && res.data.data.analysis) {
        analysisResult.value = res.data.data.analysis
        ElMessage.info('AI正在分析你的情绪...')
      } else {
        router.push('/diaries')
      }
    }
  } catch (error) {
    ElMessage.error(isEdit.value ? '修改失败' : '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchDiary()
})
</script>

<style scoped>
.diary-edit {
  max-width: 800px;
  margin: 0 auto;
}

.edit-card {
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
  gap: 30px;
  margin-bottom: 20px;
}

.emotion-label,
.emotion-score {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  color: #666;
  font-size: 14px;
}

.emotion-score {
  flex: 1;
  max-width: 300px;
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
  text-align: right;
  color: #999;
}
</style>
