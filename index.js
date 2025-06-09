import { createRouter, createWebHistory } from 'vue-router'
import { Auth } from 'aws-amplify'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/confirm',
    name: 'ConfirmRegister',
    component: () => import('../views/ConfirmRegister.vue')
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('../views/Upload.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/subscribe',
    name: 'Subscribe',
    component: () => import('../views/Subscribe.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  // 如果已登录，访问 / 或 /login 时自动跳转到 /home
  if ((to.path === '/' || to.path === '/login')) {
    try {
      await Auth.currentAuthenticatedUser()
      return next('/home')
    } catch (e) {
      // 未登录，正常进入登录页
      if (to.path === '/') return next('/login')
      return next()
    }
  }
  if (to.matched.some(record => record.meta.requiresAuth)) {
    try {
      await Auth.currentAuthenticatedUser()
      next()
    } catch (e) {
      next('/login')
    }
  } else {
    next()
  }
})

export default router 