import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/diaries',
    children: [
      {
        path: 'diaries',
        name: 'DiaryList',
        component: () => import('@/views/DiaryList.vue'),
        meta: { title: '我的日记' }
      },
      {
        path: 'diary/new',
        name: 'DiaryNew',
        component: () => import('@/views/DiaryEdit.vue'),
        meta: { title: '写日记' }
      },
      {
        path: 'diary/:id',
        name: 'DiaryDetail',
        component: () => import('@/views/DiaryDetail.vue'),
        meta: { title: '日记详情' }
      },
      {
        path: 'diary/:id/edit',
        name: 'DiaryEdit',
        component: () => import('@/views/DiaryEdit.vue'),
        meta: { title: '编辑日记' }
      },
      {
        path: 'calendar',
        name: 'Calendar',
        component: () => import('@/views/Calendar.vue'),
        meta: { title: '日历视图' }
      },
      {
        path: 'mood-trend',
        name: 'MoodTrend',
        component: () => import('@/views/MoodTrend.vue'),
        meta: { title: '心情趋势' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人信息' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth !== false && !userStore.isLoggedIn) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && userStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
