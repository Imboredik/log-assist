import { defineStore } from 'pinia'
import api from '@/composables/useApi'

export const useChatStore = defineStore('chat', {
  state: () => ({
    activeChatId: null,
    activeChatMessages: [],
    todayChats: [],
    yesterdayChats: [],
    earlierChats: [],
    loadingChats: false,
    isLoadingMessages: false,
    isBotTyping: false,
    newMessage: null,
    isSidebarCollapsed: false,
    isSending: false,
    messageInput: '',
  }),
  actions: {
    async loadChat(chatId) {
      try {
        const numericChatId = Number(chatId);
        this.isLoadingMessages = true;
        this.activeChatId = numericChatId;
        
        if (!window.location.search.includes('chat_id')) {
          const newUrl = `${window.location.pathname}?chat_id=${numericChatId}`;
          window.history.pushState({}, '', newUrl);
        }
        
        const response = await api.getChat(numericChatId);
        this.activeChatMessages = Array.isArray(response.data) 
          ? response.data.map(msg => ({
              id: msg.id,
              sender: msg.sender_type === 'user' ? 'user' : 'ai',
              text: msg.content,
              timestamp: msg.date_of_create,
              isTypingComplete: true,
              images: msg.images_url || [] // Добавляем изображения
            }))
            .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
          : [];
      } catch (error) {
        console.error('Error loading chat:', error);
        this.activeChatMessages = [{
          sender: 'ai',
          text: 'Не удалось загрузить чат. Пожалуйста, попробуйте позже.',
          isTypingComplete: true
        }];
      } finally {
        this.isLoadingMessages = false;
      }
    },

    async handleChatSelected(chatData) {
      try {
        if (!chatData?.id) return

        if (window.innerWidth <= 768) {
          this.isSidebarCollapsed = true
        }
        
        this.isLoadingMessages = true
        this.activeChatId = chatData.id
        
        // Обновляем URL, если его еще нет в параметрах
        if (!window.location.search.includes('chat_id')) {
          const newUrl = `${window.location.pathname}?chat_id=${chatData.id}`;
          window.history.pushState({}, '', newUrl);
        }
        
        // Загружаем полные данные чата, включая изображения
        const response = await api.getChat(chatData.id);
        this.activeChatMessages = Array.isArray(response.data) 
          ? response.data.map(msg => ({
              id: msg.id,
              sender: msg.sender_type === 'user' ? 'user' : 'ai',
              text: msg.content,
              timestamp: msg.date_of_create,
              isTypingComplete: true,
              images: msg.images_url || [] // Добавляем изображения
            }))
            .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
          : [];
      } catch (error) {
        console.error('Error loading chat:', error)
        this.activeChatMessages = [{
          sender: 'ai',
          text: 'Не удалось загрузить чат. Пожалуйста, попробуйте позже.',
          isTypingComplete: true
        }]
      } finally {
        this.isLoadingMessages = false
      }
    },
        
    async sendMessage(msgData) {
      if ((!msgData.text?.trim() && !msgData.localImages?.length) || !msgData.chatId) return;

      const userMessageIndex = this.activeChatMessages.length;
      let messageText = msgData.text || '[Изображение]';

      try {
          // Сообщение пользователя
          const userMessage = {
              id: Date.now(),
              sender: 'user',
              text: messageText,
              images: msgData.localImages?.map(img => img.url) || [],
              timestamp: new Date().toISOString(),
              isTypingComplete: true 
          };
          this.insertMessageInOrder(userMessage);

          // Очищаем ввод сразу после добавления сообщения пользователя
          this.messageInput = '';
          if (msgData.localImages) {
              msgData.localImages = []; // Очищаем изображения
          }

          this.isSending = true;
          this.isBotTyping = true;

          const botMessage = {
              id: Date.now() + 1,
              sender: 'ai',
              text: '',
              typing: true,
              timestamp: new Date().toISOString(),
              isTypingComplete: false
          };
          this.insertMessageInOrder(botMessage);

          const token = localStorage.getItem('assist-log-token');
          if (!token) throw new Error('Токен авторизации отсутствует');

          const response = await api.sendMessage(
              msgData.text || '',
              msgData.chatId,
              msgData.localImages || []
          );

          if (response?.data?.content) {
              // Запускаем постепенный вывод текста
              await this.typeMessage(botMessage.id, response.data.content);
          } else {
              throw new Error('Неверный формат ответа от сервера');
          }
      } catch (error) {
          console.error('Ошибка:', error);
          this.activeChatMessages = this.activeChatMessages.filter((_, i) => i < userMessageIndex);
          
          const errorMessage = {
              sender: 'ai',
              text: 'Произошла ошибка при отправке сообщения. Пожалуйста, проверьте соединение и попробуйте ещё раз.',
              timestamp: new Date().toISOString(),
              isTypingComplete: true
          };
          this.insertMessageInOrder(errorMessage);
      } finally {
          this.isSending = false;
          this.isBotTyping = false;
      }
  },

    async typeMessage(messageId, text, speed = 20) {
        const message = this.activeChatMessages.find(m => m.id === messageId);
        if (!message) return;

        message.typing = true;
        message.text = '';

        for (let i = 0; i < text.length; i++) {
            if (!message.typing) break; 
            message.text += text[i];
            await new Promise(resolve => setTimeout(resolve, speed));
        }

        message.typing = false;
        message.isTypingComplete = true; 
    },

    insertMessageInOrder(message) {
        const timestamp = new Date(message.timestamp);
        let insertIndex = this.activeChatMessages.length;
        
        for (let i = 0; i < this.activeChatMessages.length; i++) {
            if (timestamp < new Date(this.activeChatMessages[i].timestamp)) {
                insertIndex = i;
                break;
            }
        }
        
        this.activeChatMessages.splice(insertIndex, 0, message);
    },

    updateMessageInOrder(updatedMessage) {
        const index = this.activeChatMessages.findIndex(m => m.id === updatedMessage.id);
        if (index !== -1) {
            this.activeChatMessages.splice(index, 1, updatedMessage);
        }
    },

    async typeText(text, index, delay = 30) {
      const targetMessage = this.activeChatMessages[index];
      let displayedText = '';
      
      for (let i = 0; i < text.length; i++) {
        displayedText += text[i];
        targetMessage.text = displayedText;
        await new Promise(r => setTimeout(r, delay));
      }
      
      targetMessage.typing = false;
    },
    
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed
    },
    
    setTypingStatus(status) {
      this.isBotTyping = status
    },
    
    async loadUserChats() {
      this.loadingChats = true
      try {
        const response = await api.getChats()
        
        if (!response || !response.data) {
          throw new Error('Неверный формат ответа от сервера')
        }

        const now = new Date()
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        const yesterday = new Date(today)
        yesterday.setDate(yesterday.getDate() - 1)
        
        const chats = (Array.isArray(response.data) ? response.data : [])
        
        const processedChats = chats.map(chat => {
          try {
            return {
              id: String(chat.id || Math.random().toString(36).substr(2, 9)),
              user_id: chat.user_id,
              name: String(chat.name || `Чат ${chat.id}`),
              date_of_create: chat.date_of_create ? new Date(chat.date_of_create) : new Date(),
              service: chat.service || null,
              summary: chat.summary || null,
              trace: chat.trace || null,
              logs: chat.logs || null
            }
          } catch (e) {
            console.error('Ошибка обработки данных чата:', chat, e)
            return {
              id: Math.random().toString(36).substr(2, 9),
              name: 'Некорректный чат',
              date_of_create: new Date(),
              service: null,
              summary: null,
              trace: null,
              logs: null
            }
          }
        })
        
        this.todayChats = processedChats
          .filter(chat => chat.date_of_create >= today)
          .sort((a, b) => b.date_of_create - a.date_of_create)
        
        this.yesterdayChats = processedChats
          .filter(chat => chat.date_of_create >= yesterday && chat.date_of_create < today)
          .sort((a, b) => b.date_of_create - a.date_of_create)
        
        this.earlierChats = processedChats
          .filter(chat => chat.date_of_create < yesterday)
          .sort((a, b) => b.date_of_create - a.date_of_create)
        
      } catch (error) {
        console.error('Ошибка загрузки чатов:', error)
        const now = new Date()
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        const yesterday = new Date(today)
        yesterday.setDate(yesterday.getDate() - 1)
        
        this.todayChats = []
        this.yesterdayChats = []
        this.earlierChats = []
      } finally {
        this.loadingChats = false
      }
    },
    
    handleChatDeleted(deletedChatId) {
      this.todayChats = this.todayChats.filter(chat => Number(chat.id) !== Number(deletedChatId))
      this.yesterdayChats = this.yesterdayChats.filter(chat => Number(chat.id) !== Number(deletedChatId))
      this.earlierChats = this.earlierChats.filter(chat => Number(chat.id) !== Number(deletedChatId))
      
      if (this.activeChatId && Number(this.activeChatId) === Number(deletedChatId)) {
        this.activeChatId = null
        this.activeChatMessages = []
      }
    }
  }
})