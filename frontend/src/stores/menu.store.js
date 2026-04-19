// menu.store.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMenuStore = defineStore('menu', () => {
    const isOpen = ref(false)
    const activeTab = ref('profile')
    
    const openMenu = (tab = 'profile') => {
        isOpen.value = true
        activeTab.value = tab
    }
    
    const closeMenu = () => {
        isOpen.value = false
    }
    
    const setActiveTab = (tab) => {
        activeTab.value = tab
    }
    
    const toggleMenu = () => {
        isOpen.value = !isOpen.value
    }
    
    return {
        isOpen,
        activeTab,
        openMenu,
        closeMenu,
        setActiveTab,
        toggleMenu
    }
})