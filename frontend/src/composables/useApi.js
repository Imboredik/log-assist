import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1', 
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('assist-log-token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(response => {
  if (response.data && typeof response.data === 'object') {
    const processUrls = (data) => {
      if (Array.isArray(data)) {
        return data.map(item => processUrls(item));
      } else if (data && typeof data === 'object') {
        return Object.fromEntries(
          Object.entries(data).map(([key, value]) => {
            if (key.endsWith('_url') || key.endsWith('Url')) {
              // Заменяем URL MinIO на проксированный путь
              if (typeof value === 'string' && value.includes('image-db:9000')) {
                return [key, value.replace('http://image-db:9000', '')];
              }
              if (Array.isArray(value)) {
                return [key, value.map(url => 
                  typeof url === 'string' && url.includes('image-db:9000') 
                    ? url.replace('http://image-db:9000', '') 
                    : url
                )];
              }
            }
            return [key, value];
          })
        );
      }
      return data;
    };
    
    return {
      ...response,
      data: processUrls(response.data)
    };
  }
  return response;
}, error => {
  return Promise.reject(error);
});

export default {
  login(credentials) {
    return api.post('/user/login', credentials)
      .then(response => {
        const data = response.data;
        return {
          data: {
            token: data.token,
            user: {
              username: data.username,
              email: data.email,
              role: data.role,
              avatarUrl: data.avatar_url,
              date_of_create: data.date_of_create
            }
          }
        }
      });
  },
  
  register(userData) {
    return api.post('/user/register', {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        role_id: userData.role_id
    }).then(response => {
        const data = response.data;
        return {
            data: {
                token: data.token,
                user: {
                    username: data.username,
                    email: data.email,
                    role: data.role,
                    date_of_create: data.date_of_create,
                    avatarUrl: data.avatar_url
                }
            }
        }
    });
  },

  getUser() {
    return api.get('/user').then(response => {
      return {
        username: response.data.username,
        email: response.data.email,
        role: response.data.role,
        dateOfRegistration: response.data.date_of_create,
        avatar_url: response.data.avatar_url
      };
    });
  },

  getRoles() {
    return api.get('/roles')
      .then(response => {
        return {
          data: response.data.map(role => ({
            id: role.id,
            role: role.role,
            description: role.description || (role.prompt ? role.prompt.split('\n')[0] : 'Описание отсутствует'),
          }))
        }
      })
      .catch(error => {
        console.error('Error fetching roles:', error)
        return { data: [] }
      })
  },

  async sendMessage(message, chatId, images = []) {
    if (!chatId) throw new Error('chatId is required');

    const queryParams = new URLSearchParams({
      chat_id: chatId,
      message: message || ''
    }).toString();

    if (images.length === 0) {
      // Только текст — без тела
      return api.post(`/message?${queryParams}`);
    } else {
      // С изображениями
      const formData = new FormData();
      images.forEach(image => {
        formData.append('images', image.file);
      });

      return api.post(`/message?${queryParams}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    }
  },

  getChats() {
    return api.get('/user/chats')
  },

  getChat(chatId) {
    return api.get('/chat', {
      params: {
        chat_id: chatId
      }
    }).then(response => {
      // Обработка изображений
      const messages = Array.isArray(response.data) ? response.data : []
      return {
        data: messages.map(msg => ({
          ...msg,
          images: msg.images_url || []
        }))
      }
    })
  },

  getAnalysis(chatId) {
    return api.post('/message/analysis', null, {
      params: { chat_id: chatId }
    })
  },

  getSolution(chatId) {
    return api.post('/message/solution', null, {
      params: { chat_id: chatId }
    })
  },

  deleteChat(chatId) {
    return api.delete('/chat', {
      params: {
        chat_id: chatId
      }
    });
  },

  downloadChat(chatId) {
    return api.get('/chat', {
      params: {
        chat_id: chatId
      }
    });
  },

  updateUserProfile(updateData) {
    return api.patch('/user', updateData);
  },

  updateUserName(newName) {
    return api.post('/user/name', { 
      username: newName 
    }).then(response => {
      return response.data;
    });
  },

  updateUserEmail(newEmail) {
    return api.post('/user/email', { email: newEmail })
      .then(response => {
        return response.data;
      });
  },

  updateUserPassword(currentPassword, newPassword) {
    return api.post('/user/password', { 
      old_password: currentPassword,
      new_password: newPassword
    }).then(response => {
      return response.data;
    });
  },

  updateUserAvatar(avatarFile) {
    const formData = new FormData();
    formData.append('file', avatarFile);
    
    return api.post('/user/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }).then(response => {
      return {
        token: response.data.token,
        user: {
          username: response.data.username,
          email: response.data.email,
          role: response.data.role,
          avatarUrl: response.data.avatar_url,
          date_of_create: response.data.date_of_create
        }
      };
    });
  },

  deleteUserAvatar() {
    return api.delete('/user/avatar').then(response => {
      console.log('Avatar delete response:', response.data);
      return response;
    });
  },

  getPriorities() {
    return api.get('/priorities')
      .then(response => {
        return {
          data: response.data.map(priority => ({
            priority_id: priority.id,
            name: priority.priority,
          }))
        };
      })
      .catch(error => {
        console.error('Error fetching priorities:', error);
        throw error;
      });
  },

  
  getTickets() {
    return api.get('/tickets')
      .then(response => {
        return {
          data: response.data.map(ticket => ({
            id: ticket.id, 
            chat_id: ticket.chat_id,
            priority_id: ticket.priority_id,
            priority: ticket.priority,
            service: ticket.service,
            summary: ticket.summary,
            trace: ticket.trace,
            back_logs: ticket.back_logs,
            front_logs: ticket.front_logs,
            user_id: ticket.user_id,
            username: ticket.username,
            email: ticket.email,
            role_id: ticket.role_id,
            role: ticket.role,
            date_of_create: ticket.date_of_create
          }))
        }
      })
      .catch(error => {
        console.error('Error fetching tickets:', error)
        throw error
      })
  },

  getTicket(ticketId) {
    return api.get('/ticket', {
      params: {
        ticket_id: ticketId
      }
    })
    .then(response => {
      const ticket = response.data;
      return {
        data: {
          id: ticket.id, 
          chat_id: ticket.chat_id,
          priority_id: ticket.priority_id,
          priority: ticket.priority,
          service: ticket.service,
          summary: ticket.summary,
          trace: ticket.trace,
          back_logs: ticket.back_logs,
          front_logs: ticket.front_logs,
          user_id: ticket.user_id,
          username: ticket.username,
          email: ticket.email,
          role_id: ticket.role_id,
          role: ticket.role,
          date_of_create: ticket.date_of_create
        }
      }
    })
    .catch(error => {
      console.error('Error fetching ticket:', error)
      throw error
    })
  },

 getTicketInit(chatId) {
    const params = {};
    if (chatId && !isNaN(chatId)) {
      params.chat_id = Number(chatId);
    }
    return api.get('/ticket/init', { params });
  },


  createTicket(ticketData) {
    return api.post('/ticket', ticketData)
  },

  updateTicket(ticketData) {
      return api.post('/ticket/update', ticketData)
  },

  downloadTicketFile: async (ticketId, fileType) => {
    try {
      const response = await api.get(`/ticket/download`, {
        params: {
          ticket_id: ticketId,
          file_type: fileType
        },
        responseType: 'blob'
      });
      
      return response;
    } catch (err) {
      console.error('Download error:', err);
      throw err;
    }
  }
}