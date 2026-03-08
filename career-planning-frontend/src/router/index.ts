import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/modules/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/CUserLogin.vue'),//登录
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/CUserRegister.vue'),//注册
    },
    {
      path: '/forgot-password',
      name: 'forget-password',
      component: () => import('../views/CUserForgetPassword.vue'),//忘记密码
    },
    {
      path: '/',
      component: () => import('../components/Layout.vue'), // 布局组件
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('../views/HomePage.vue'), // 首页
        },
        {
          path: 'upload',
          name: 'upload',
          component: () => import('../views/Upload.vue'),
        },
        {
          path: 'report',
          name: 'report',
          component: () => import('../views/Report.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/404.vue')//404错误
    },
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