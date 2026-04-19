import { defineStore } from 'pinia'
import api from '@/composables/useApi'
import router from '@/router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('assist-log-token') || null,
    user: null,
    isAuthenticated: false,
    pendingChatId: localStorage.getItem('pending_chat_id') || null
  }),
  actions: {
    async checkAuth() {
      if (!this.token || this.token === 'placeholder-token') {
        this.isAuthenticated = false
        return false
      }
      
      try {
        const user = await api.getUser()
        console.log('User data received:', user);
        this.user = {
          ...user,
          avatarUrl: user.avatar_url || null
        }
        this.isAuthenticated = true
        
        // Проверяем, открыто ли через расширение
        const urlParams = new URLSearchParams(window.location.search);
        const isExtensionRequest = urlParams.get('extension') === 'true';
        
        if (isExtensionRequest) {
          // Возвращаем токен, если запрос от расширения
          return this.token;
        }
        
        return true
      } catch (error) {
        if (error.response?.status === 400 || error.response?.status === 401) {
          this.logout()
          return false
        }
        throw error
      }
    },
    
    async login(credentials) {
        try {
            const response = await api.login(credentials);
            const token = response.data?.token;

            if (!token) {
            console.error("Токен не получен — login отменён", response);
            return false;
            }

            this.token = token;
            this.isAuthenticated = true;
            localStorage.setItem('assist-log-token', token);

            const urlParams = new URLSearchParams(window.location.search);
            const isExtensionRequest = urlParams.get('extension') === 'true';
            const sourceTabId = urlParams.get('sourceTabId');

            if (isExtensionRequest) {
            // Улучшенная отправка токена с таймаутом 10 секунд
            await new Promise((resolve) => {
                let ackReceived = false;
                let timer;

                const sendToken = async () => {
                try {
                    // Пробуем chrome.runtime
                    if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
                    await new Promise((resolve, reject) => {
                        chrome.runtime.sendMessage({
                        action: "authSuccess",
                        token,
                        sourceTabId
                        }, (response) => {
                        if (chrome.runtime.lastError) {
                            reject(chrome.runtime.lastError);
                        } else {
                            resolve(response);
                        }
                        });
                    });
                    return true;
                    }
                    return false;
                } catch (e) {
                    console.error('Error sending via chrome.runtime:', e);
                    return false;
                }
                };

                const sendViaPostMessage = () => {
                window.postMessage({
                    type: "ASSIST_LOG_AUTH",
                    token,
                    sourceTabId
                }, "*");
                return true;
                };

                const waitForAck = () => {
                const ackListener = (event) => {
                    if (event.data?.type === "ASSIST_LOG_AUTH_ACK") {
                    ackReceived = true;
                    window.removeEventListener("message", ackListener);
                    clearTimeout(timer);
                    resolve();
                    window.close();
                    }
                };
                window.addEventListener("message", ackListener);
                };

                // Таймаут 10 секунд
                timer = setTimeout(() => {
                if (!ackReceived) {
                    console.warn("Timeout waiting for ACK, closing window");
                    resolve();
                    window.close();
                }
                }, 10000);

                // Ждем подтверждения получения
                waitForAck();

                // Пробуем оба метода отправки
                sendToken().then(success => {
                if (!success) {
                    sendViaPostMessage();
                }
                });
            });
            return;
            }

            router.push('/chat');
            return response.data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
        },

    async register(userData) {
      try {
          const response = await api.register(userData);
          if (response.data?.token) {
              this.token = response.data.token;
              this.isAuthenticated = true;
              localStorage.setItem('assist-log-token', response.data.token);
              return response;
          }
      } catch (error) {
          console.error("Ошибка регистрации:", error.response?.data || error.message);
          throw new Error(error.response?.data?.detail || "Произошла ошибка при регистрации");
      }
  },

    async updateUserProfile(updateData) {
    try {
      const response = await api.updateUserProfile(updateData);
      this.user = {
        ...this.user,
        ...response.data.user
      };
      return response;
    } catch (error) {
      console.error('Profile update error:', error);
      throw error;
    }
  },

  async updateUserAvatar(file) {
    try {
      const response = await api.updateUserAvatar(file);
      this.user.avatarUrl = response.user.avatarUrl;
      // this.user.role = response.user.role;
      return response;
    } catch (error) {
      console.error('Avatar upload failed:', error);
      throw error;
    }
  },

  async updateUserName(newName) {
    try {
      const response = await api.updateUserName(newName);
      this.user.username = newName;
      if (response.token) {
        this.token = response.token;
        localStorage.setItem('assist-log-token', response.token);
      }
      return response;
    } catch (error) {
      console.error('Error updating username:', error);
      throw error;
    }
  },

  async updateUserEmail(newEmail) {
    try {
      const response = await api.updateUserEmail(newEmail);
      this.user.email = newEmail;
      // Сервер всегда возвращает новый токен при изменении email
      if (response.token) {
        this.token = response.token;
        localStorage.setItem('assist-log-token', response.token);
      }
      return response;
    } catch (error) {
      console.error('Error updating email:', error);
      throw error;
    }
  },

  async updateUserPassword(currentPassword, newPassword) {
    try {
      const response = await api.updateUserPassword(currentPassword, newPassword);
      // Сервер всегда возвращает новый токен при изменении пароля
      if (response.token) {
        this.token = response.token;
        localStorage.setItem('assist-log-token', response.token);
      }
      return response;
    } catch (error) {
      console.error('Error updating password:', error);
      throw error;
    }
  },

  async deleteUserAvatar() {
    try {
      await api.deleteUserAvatar();
      this.user.avatarUrl = null;
    } catch (error) {
      console.error('Avatar delete error:', error);
      throw error;
    }
  },

  logout() {
      this.token = null
      this.isAuthenticated = false
      this.user = null
      localStorage.removeItem('assist-log-token')
      window.location.reload()
  },

    setPendingChatId(chatId) {
      this.pendingChatId = chatId
      if (chatId) {
        localStorage.setItem('pending_chat_id', chatId)
      } else {
        localStorage.removeItem('pending_chat_id')
      }
    }
  },
  getters: {
    getToken: (state) => state.token
  }
})