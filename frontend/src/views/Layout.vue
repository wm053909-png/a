<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="layout-aside">
      <div class="logo">
        <h1> AI心情日记</h1>
      </div>
      <el-menu
        :default-active="route.path"
        router
        class="aside-menu"
      >
        <el-menu-item index="/diaries">
          <el-icon><Notebook /></el-icon>
          <span>我的日记</span>
        </el-menu-item>
        <el-menu-item index="/diary/new">
          <el-icon><EditPen /></el-icon>
          <span>写日记</span>
        </el-menu-item>
        <el-menu-item index="/calendar">
          <el-icon><Calendar /></el-icon>
          <span>日历视图</span>
        </el-menu-item>
        <el-menu-item index="/mood-trend">
          <el-icon><TrendCharts /></el-icon>
          <span>心情趋势</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <h2>{{ route.meta.title || 'AI心情日记' }}</h2>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click">
            <span class="user-info">
              <el-avatar :size="32" :src="userAvatar">
                {{ userStore.userInfo?.nickname?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="username">{{ userStore.userInfo?.nickname || '用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">
                  <el-icon><User /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Notebook, EditPen, Calendar, TrendCharts,
  ArrowDown, User, SwitchButton
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const userAvatar = computed(() => {
  return userStore.userInfo?.avatar || ''
})

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.layout-aside {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h1 {
  font-size: 18px;
  color: white;
  white-space: nowrap;
}

.aside-menu {
  border-right: none;
  background: transparent;
}

.aside-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.8);
}

.aside-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.aside-menu .el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.layout-header {
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 0 20px;
}

.header-left h2 {
  font-size: 18px;
  color: #333;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 8px;
  transition: background 0.3s;
}

.user-info:hover {
  background: #f5f7fa;
}

.username {
  margin: 0 8px;
  color: #333;
}

.layout-main {
  background: #f5f7fa;
  padding: 20px;
}
</style>
