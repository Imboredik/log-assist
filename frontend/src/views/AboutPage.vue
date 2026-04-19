<template>
  <div class="about-container" :class="{ 'night-mode': uiStore.isNightMode }">
    <div class="about-card">
      <div class="header">
        <h1>Log<span class="ai">Assist</span></h1>
        <p class="subtitle">Ваш интеллектуальный помощник для работы с логами</p>
      </div>
      
      <div class="features">
        <div class="feature-card" v-for="feature in features" :key="feature.title">
          <div class="feature-icon">
            <Icon :icon="feature.icon" width="32" height="32" />
          </div>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </div>
        
        <!-- Кнопка как 6-й элемент сетки -->
        <div class="feature-card cta-card">
          <div class="feature-icon">
            <Icon icon="mdi:rocket-launch" width="32" height="32" />
          </div>
          <h3>Готовы начать?</h3>
          <button @click="goToLogin" class="cta-button">
            Начать работу
            <Icon icon="mdi:arrow-right" width="20" height="20" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Icon } from '@iconify/vue'
import { useRouter } from 'vue-router'
import { useUIStore } from '@/stores/ui.store'

const router = useRouter()
const uiStore = useUIStore()

const features = [
  {
    icon: 'mdi:robot',
    title: 'AI-анализ логов',
    description: 'Автоматическое выявление проблем и аномалий в логах'
  },
  {
    icon: 'mdi:history',
    title: 'История запросов',
    description: 'Все ваши диалоги сохраняются для последующего анализа'
  },
  {
    icon: 'mdi:ticket-outline',
    title: 'Автоматические тикеты',
    description: 'Генерация тикетов на основе анализа логов'
  },
  {
    icon: 'mdi:shield-lock',
    title: 'Безопасность',
    description: 'Ваши данные защищены современными методами шифрования'
  },
  {
    icon: 'mdi:lightning-bolt',
    title: 'Быстрое решение',
    description: 'Мгновенные ответы на ваши вопросы по логам'
  }
]

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.about-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 20px;
  background-color: var(--color-background);
  transition: background-color 0.3s ease;
  box-sizing: border-box;
}

.about-card {
  max-width: 1500px;
  width: 100%;
  height: calc(100vh - 40px); 
  max-height: 800px;
  background-color: var(--panel-bg);
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--color-border);
  transition: all 0.3s ease;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}


h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
}

.ai {
  color: #7800FF;
}

.subtitle {
  font-size: 1rem;
  color: var(--color-text);
  opacity: 0.8;
  margin-bottom: 1.5rem;
  transition: color 0.3s ease;
}

.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin: 0;
  flex-grow: 1;
  min-height: 0;
  overflow-y: auto;
  padding-bottom: 20px;
  grid-auto-rows: minmax(180px, 1fr);
  padding: 10px;
  margin: -10px; 
}

.feature-card {
  padding: 16px; 
  border-radius: 12px;
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
  max-height: 250px; 
  box-sizing: border-box;
  margin: 10px;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  border-color: #7800FF;
  margin: 15px 10px 5px 10px;
}

.feature-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background-color: rgba(120, 0, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 12px;
  color: #7800FF;
}

.feature-card h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--color-text);
  transition: color 0.3s ease;
}

.feature-card p {
  color: var(--color-text);
  opacity: 0.8;
  font-size: 0.9rem;
  line-height: 1.5;
  transition: color 0.3s ease;
  flex-grow: 1;
  margin-bottom: 15px; 
}

.cta-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px;
  width: 100%;
  background-color: #7800FF;
  color: white;
  border-radius: 8px;
  border: none;
  font-weight: 500;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: auto;
}

.cta-button:hover {
  background-color: #6000CC;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(120, 0, 255, 0.3);
}

/* Ночной режим */
.night-mode .feature-card {
  background-color: var(--color-background-mute);
}

.night-mode .feature-card:hover {
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

@media (max-width: 1600px) {
  .about-card {
    max-height: calc(100vh - 40px);
    padding: 25px;
  }
  
  .feature-card {
    min-height: 180px; 
  }
  
  .features {
    grid-auto-rows: minmax(160px, 1fr);
    gap: 18px;
  }
}

@media (max-width: 1400px) {
  .features {
    grid-template-columns: repeat(2, 1fr);
    grid-auto-rows: minmax(160px, 220px);
  }
  
  .about-card {
    padding: 30px;
  }
}

@media (max-width: 1024px) {
  .features {
    grid-auto-rows: minmax(150px, 200px);
    gap: 16px;
  }
  
  .feature-card {
    min-height: 220px;
  }
}

@media (max-width: 768px) {
  .about-container {
    padding: 15px;
  }

  .about-card {
    padding: 20px;
    max-height: calc(100vh - 30px);
  }
  
  h1 {
    font-size: 1.8rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .features {
    grid-template-columns: 1fr;
    grid-auto-rows: auto; 
    gap: 14px;
  }
  
  .feature-card {
    max-height: none; 
    min-height: 160px;
    padding: 15px;
  }

   h1 {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .about-card {
    padding: 15px;
  }
  
  .header {
    margin-bottom: 20px;
  }
  
  .feature-card {
    padding: 12px;
    min-height: 140px;
  }
  
  .feature-icon {
    width: 40px;
    height: 40px;
  }
}
</style>