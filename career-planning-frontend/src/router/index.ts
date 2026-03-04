import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../components/LoginView.vue'), // 首页直接显示登录页
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../components/Register.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../components/LoginView.vue'),
    },
    {
      path: '/forgot-password',
      name: 'forget-password',
      component: () => import('../components/ForgetPassword.vue'),
    }
   
  ],
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  try {
    const userStore = useUserStore()
    if (to.name === 'login' && userStore.isAuthenticated) {
      const redirect = to.query.redirect as string
      next(redirect || { name: 'home' })
      return
    }
    if (to.meta.requiresAuth && !userStore.isAuthenticated) {
      next({ name: 'login', query: { redirect: to.fullPath } })
    } else {
      next()
    }
  } catch (error) {
    console.error('路由守卫错误:', error)
    next()
  }
})

export default router