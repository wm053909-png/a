import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  // 登录
  async function login(username, password) {
    const res = await api.post('/api/auth/login', { username, password })
    if (res.data.code === 200) {
      token.value = res.data.data.token
      userInfo.value = res.data.data.user
      localStorage.setItem('token', token.value)
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
      return true
    }
    throw new Error(res.data.message)
  }

  // 注册
  async function register(data) {
    const res = await api.post('/api/auth/register', data)
    if (res.data.code === 200) {
      return true
    }
    throw new Error(res.data.message)
  }

  // 获取用户信息
  async function fetchProfile() {
    const res = await api.get('/api/auth/user/profile')
    if (res.data.code === 200) {
      userInfo.value = res.data.data
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    }
  }

  // 更新用户信息
  async function updateProfile(data) {
    const res = await api.put('/api/auth/user/profile', data)
    if (res.data.code === 200) {
      userInfo.value = res.data.data
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
      return true
    }
    throw new Error(res.data.message)
  }

  // 退出登录
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    login,
    register,
    fetchProfile,
    updateProfile,
    logout
  }
})
