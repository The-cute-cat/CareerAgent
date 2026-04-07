import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/modules/user'
import { userGetUserInfoService } from '@/api/user/user'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/CUserLogin.vue'), //登录
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/CUserRegister.vue'), //注册
  },
  {
    path: '/forgot-password',
    name: 'forget-password',
    component: () => import('../views/CUserForgetPassword.vue'), //忘记密码
  },
  {
    path: '/welcome',
    name: 'welcome',
    component: () => import('../views/LandingPage.vue'), // 未登录欢迎页（独立页面，无Layout）
  },
  {
    path: '/resume-editor',
    name: 'resume-editor',
    component: () => import('../views/ResumeEditor.vue'),
  },
  {
    path: '/',
    component: () => import('../components/Layout.vue'), // 布局组件
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('../views/CHomePage.vue'), // 首页（登录后）
      },
      {
        path: 'career-form',
        redirect: { name: 'career-form-resume' },
      },
      {
        path: 'career-form/resume',
        name: 'career-form-resume',
        component: () => import('../views/CareerForm.vue'),
      },
      {
        path: 'career-form/template',
        name: 'career-form-template',
        component: () => import('../views/CareerForm.vue'),
      },
      {
        path: 'resume-template',
        name: 'resume-template',
        component: () => import('../views/ResumeTemplate.vue'),
        meta: { title: '简历模板生成' }
      },
      {
        path: 'report',
        name: 'report',
        component: () => import('../views/CReport.vue'),
      },
      {
        path: 'development-map',
        name: 'development-map',
        component: () => import('../views/DevelopmentMap.vue'),
      },
      {
        path: 'knowledge-base',
        name: 'knowledge-base',
        component: () => import('../views/JobKnowledge.vue'),
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('../views/CProfile.vue'),
      },
      {
        path: 'job-matching',
        name: 'job-matching',
        component: () => import('../views/JobMatching.vue'),
      },
      {
        path: 'job-position',
        name: 'job-position',
        component: () => import('../components/JobMatching_Position.vue'),
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('../views/CProfile.vue'),
        meta: { title: '设置中心' }
      },
      {
        path: 'interviews/:type?',
        name: 'interviews',
        component: () => import('../views/CInterviews.vue'),
        meta: { title: '我的面试' }
      },
      {
        path: 'admin',
        name: 'admin',
        component: () => import('../components/AdminManager/AdminPanel.vue'),
        meta: { title: '管理后台' }
      },
    ],
  },
  // {
  //   path: '/:pathMatch(.*)*',
  //   name: 'NotFound',
  //   component: () => import('../views/404.vue'), //404错误
  // },
]

const router = createRouter({
  history: createWebHistory(),
  routes: routes
})

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  try {
    const userStore = useUserStore()
    if (userStore.isLoggedIn && !userStore.userInfo) {
      try {
        const res = await userGetUserInfoService()
        userStore.userInfo = res.data.data.checkUser
      } catch (error) {
        userStore.clearUserALLInfo()
      }
    }

    // 延迟执行以确保 Pinia 持久化状态已恢复
    const checkAuth = () => {
      const isLoggedIn = userStore.isLoggedIn

      // 已登录用户访问登录页或欢迎页，重定向到首页
      if ((to.name === 'login' || to.name === 'welcome') && isLoggedIn) {
        const redirect = to.query.redirect as string
        next(redirect || { name: 'home' })
        return
      }

      // 未登录用户访问首页，重定向到欢迎页
      if (to.name === 'home' && !isLoggedIn) {
        next({ name: 'welcome' })
        return
      }

      // 需要认证但未登录，重定向到登录页
      if (to.meta.requiresAuth && !isLoggedIn) {
        next({ name: 'login', query: { redirect: to.fullPath } })
        return
      }

      // 其他情况正常放行
      next()
    }

    // 使用微任务队列确保状态恢复后再检查
    Promise.resolve().then(checkAuth)
  } catch (error) {
    console.error('路由守卫错误:', error)
    // 发生错误时放行，避免用户被卡在空白页
    next()
  }
})

export default router