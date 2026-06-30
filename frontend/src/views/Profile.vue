<template>
  <div class="profile-page">
    <el-card class="profile-card">
      <template #header>
        <h2>个人信息</h2>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名">
          <el-input :value="userStore.userInfo?.username" disabled />
        </el-form-item>

        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-divider>修改密码</el-divider>

        <el-form-item label="原密码" prop="old_password">
          <el-input
            v-model="form.old_password"
            type="password"
            placeholder="请输入原密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="form.new_password"
            type="password"
            placeholder="请输入新密码（至少6位）"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="form.confirm_password"
            type="password"
            placeholder="请确认新密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">
            保存修改
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="stats-card">
      <template #header>
        <h2>我的统计</h2>
      </template>

      <div class="user-stats">
        <div class="stat-item">
          <span class="value">{{ stats.diaryCount }}</span>
          <span class="label">日记总数</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ stats.daysCount }}</span>
          <span class="label">写日记天数</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ stats.avgScore }}</span>
          <span class="label">平均情绪得分</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import api from '@/api'

const userStore = useUserStore()
const formRef = ref(null)
const saving = ref(false)

const form = reactive({
  nickname: '',
  email: '',
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const stats = reactive({
  diaryCount: 0,
  daysCount: 0,
  avgScore: 0
})

const validateConfirmPassword = (rule, value, callback) => {
  if (form.new_password && value !== form.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  old_password: [
    { validator: (rule, value, callback) => {
      if (form.new_password && !value) {
        callback(new Error('请输入原密码'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ],
  new_password: [
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const fetchProfile = async () => {
  try {
    await userStore.fetchProfile()
    const info = userStore.userInfo
    if (info) {
      form.nickname = info.nickname || ''
      form.email = info.email || ''
    }
  } catch (error) {
    console.error('获取用户信息失败')
  }
}

const fetchStats = async () => {
  try {
    const res = await api.get('/api/stats/emotion')
    if (res.data.code === 200) {
      stats.diaryCount = res.data.data.total

      // 计算平均情绪得分
      const emotions = res.data.data.emotions
      if (emotions.length > 0) {
        const totalScore = emotions.reduce((sum, e) => sum + (e.emotion_score || 0.5) * e.count, 0)
        stats.avgScore = (totalScore / stats.diaryCount).toFixed(2)
      }

      // 获取写日记天数
      const calendarRes = await api.get('/api/stats/calendar', {
        params: {
          year: new Date().getFullYear(),
          month: new Date().getMonth() + 1
        }
      })
      if (calendarRes.data.code === 200) {
        stats.daysCount = calendarRes.data.data.days.length
      }
    }
  } catch (error) {
    console.error('获取统计信息失败')
  }
}

const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  // 检查是否需要修改密码
  if (form.new_password && !form.old_password) {
    ElMessage.error('请输入原密码')
    return
  }

  saving.value = true
  try {
    const updateData = {
      nickname: form.nickname,
      email: form.email
    }

    if (form.new_password) {
      updateData.password = form.new_password
      updateData.old_password = form.old_password
    }

    await userStore.updateProfile(updateData)
    ElMessage.success('修改成功')

    // 清空密码字段
    form.old_password = ''
    form.new_password = ''
    form.confirm_password = ''
  } catch (error) {
    ElMessage.error(error.message || '修改失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchProfile()
  fetchStats()
})
</script>

<style scoped>
.profile-page {
  max-width: 800px;
  margin: 0 auto;
}

.profile-card,
.stats-card {
  margin-bottom: 20px;
}

.profile-card h2,
.stats-card h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
}

.stat-item .value {
  display: block;
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-item .label {
  color: #666;
  font-size: 14px;
}
</style>
