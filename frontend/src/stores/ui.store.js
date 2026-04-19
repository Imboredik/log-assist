import { defineStore } from 'pinia'

export const useUIStore = defineStore('ui', {
  state: () => ({
    isNightMode: false,
    message: null,
    isError: false,
    userThemeChoice: null,
    // Добавляем состояние меню
    menu: {
      isOpen: false,
      activeTab: 'profile'
    },
    // Добавляем состояние подписки
    subscription: {
      currentPlan: 'free',
      plans: {
        free: {
          name: 'Бесплатная',
          price: 0,
          features: [
            'Базовые функции',
            'Ограниченное количество запросов',
            'Поддержка по email'
          ]
        },
        basic: {
          name: 'Базовая',
          price: 299,
          features: [
            'Все базовые функции',
            'Увеличенное количество запросов',
            'Приоритетная поддержка'
          ]
        },
        pro: {
          name: 'Профессиональная',
          price: 999,
          features: [
            'Все функции без ограничений',
            'Неограниченное количество запросов',
            'Персональный менеджер',
            'Высокий приоритет поддержки'
          ]
        }
      }
    }
  }),

  actions: {

    initializeTheme() {

      const savedTheme = localStorage.getItem('nightMode')

      if (savedTheme !== null) {

        this.isNightMode = savedTheme === 'true'
        this.userThemeChoice = true
      } else {
        this.isNightMode = window.matchMedia('(prefers-color-scheme: dark)').matches
        this.userThemeChoice = false
      }
      
      this.applyTheme()
    },
    
    toggleNightMode() {
      this.isNightMode = !this.isNightMode
      this.userThemeChoice = true
      localStorage.setItem('nightMode', this.isNightMode)
      this.applyTheme()
    },
    
    applyTheme() {
      if (this.isNightMode) {
        document.documentElement.classList.add('night-mode')
        document.documentElement.style.setProperty('color-scheme', 'dark')
      } else {
        document.documentElement.classList.remove('night-mode')
        document.documentElement.style.setProperty('color-scheme', 'light')
      }
    },
    
    showMessage(msg, error = false) {
      this.message = msg
      this.isError = error
      setTimeout(() => {
        this.message = null
      }, 5000)
    },

    // Методы для управления меню
    openMenu(tab = 'profile') {
        this.menu.isOpen = true
        this.menu.activeTab = tab
        console.log('Opening menu with tab:', tab)
    },

    closeMenu() {
      this.menu.isOpen = false
    },

    changeSubscription(plan) {
      this.subscription.currentPlan = plan
    }
  }
})