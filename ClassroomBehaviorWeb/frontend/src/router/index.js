import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/userStore'

const routes = [
  { path: '/', redirect: '/login' },
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
  // { 
  //   path: '/detect', 
  //   name: 'Detect', 
  //   component: () => import('@/views/Detect.vue'), 
  //   meta: { requiresAuth: true } 
  // },
  { 
    path: '/history', 
    name: 'History', 
    component: () => import('@/views/History.vue'), 
    meta: { requiresAuth: true } 
  },
  
  { 
    path: '/:pathMatch(.*)*', 
    name: '404', 
    component: () => import('@/views/404.vue') 
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫（自动适配新增的视频检测路由权限控制）
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  console.log('路由守卫：', to.path, '是否需要登录：', to.meta.requiresAuth, '当前登录状态：', userStore.isLoggedIn)
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    console.log('未登录，跳转至登录页')
    next('/login')
  } else {
    console.log('允许访问：', to.path)
    next()
  }
})

export default router