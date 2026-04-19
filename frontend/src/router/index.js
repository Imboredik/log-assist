import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import ErrorPage from '../views/ErrorPage.vue'
import AuthPage from '../views/AuthPage.vue'
import AboutPage from '../views/AboutPage.vue'
import { useAuthStore } from '@/stores/auth.store'

const routes = [
  {
    path: '/',
    redirect: '/about'
  },

  {
    path: '/about',
    component: AboutPage,
    meta: { requiresAuth: false }
  },

  {
    path: '/chat',
    component: ChatView,
    meta: { requiresAuth: true },
    props: (route) => ({ chatId: route.query.chat_id })
  },

  {
    path: '/login',
    component: AuthPage,
    meta: { requiresAuth: false }
  },

  {
    path: '/register',
    component: AuthPage,
    meta: { requiresAuth: false },
    props: { initialTab: 'register' }
  },

  {
    path: '/error',
    component: ErrorPage,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const isFirstVisit = !localStorage.getItem('visitedBefore')
  
  if (isFirstVisit && to.path !== '/about') {
    localStorage.setItem('visitedBefore', 'true')
    return next('/about')
  }

  if (!to.meta.requiresAuth) {
    return next()
  }

  const token = localStorage.getItem('assist-log-token')

  // Проверяем placeholder-токен
  if (token === 'placeholder-token') {
    return next()
  }

  try {
    const isAuthenticated = await authStore.checkAuth()
    
    if (isAuthenticated) {
      if (to.path === '/login' || to.path === '/register') {
        return next('/chat')
      }
      return next()
    } else {
      if (to.path !== '/login' && to.path !== '/register') {
        return next('/login')
      }
      return next()
    }
  } catch (error) {
    console.error('Ошибка проверки аутентификации:', error)
    if (to.path !== '/login' && to.path !== '/register') {
      if (to.query.chat_id) {
        authStore.setPendingChatId(to.query.chat_id)
      }
      return next('/login')
    }
    return next()
  }
})

export default router