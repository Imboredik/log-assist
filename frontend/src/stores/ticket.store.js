import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/composables/useApi'

export const useTicketStore = defineStore('ticket', () => {
    const tickets = ref([])
    const currentTicket = ref(null)
    const isLoading = ref(false)
    const error = ref(null)
    const isChatSelectionOpen = ref(false)
    const isEditorOpen = ref(false)

    const fetchTickets = async () => {
        isLoading.value = true
        try {
            const response = await api.getTickets()
            tickets.value = response.data
        } catch (err) {
            error.value = err.response?.data?.detail || 'Ошибка загрузки тикетов'
        } finally {
            isLoading.value = false
        }
    }

    const openTicketEditor = async (chatId) => {
        isLoading.value = true
        try {
            const response = await api.getTicketInit(chatId)
            currentTicket.value = response.data
            isEditorOpen.value = true
            isChatSelectionOpen.value = false
            return true
        } catch (err) {
            error.value = err.response?.data?.detail || 'Ошибка инициализации тикета'
            return false
        } finally {
            isLoading.value = false
        }
    }

    const openChatSelection = () => {
        isChatSelectionOpen.value = true
        isEditorOpen.value = false
    }

    const saveTicket = async (ticketData) => {
        isLoading.value = true
        try {
            let response;
            if (currentTicket.value?.id) { 
                // Обновление существующего тикета
                response = await api.updateTicket({
                    id: currentTicket.value.id,
                    chat_id: ticketData.chat_id,
                    priority_id: ticketData.priority_id,
                    service: ticketData.service,
                    summary: ticketData.summary,
                    trace: ticketData.trace,
                    back_logs: ticketData.back_logs,
                    front_logs: ticketData.front_logs
                })
            } else {
                // Создание нового тикета
                response = await api.createTicket({
                    chat_id: ticketData.chat_id,
                    priority_id: ticketData.priority_id,
                    service: ticketData.service,
                    summary: ticketData.summary,
                    trace: ticketData.trace,
                    back_logs: ticketData.back_logs,
                    front_logs: ticketData.front_logs
                })
            }
            
            currentTicket.value = response.data
            await fetchTickets()
            isEditorOpen.value = false
            return true
        } catch (err) {
            error.value = err.response?.data?.detail || 'Ошибка сохранения тикета'
            return false
        } finally {
            isLoading.value = false
        }
    }

    const openTicketView = async (ticketId) => {
    isLoading.value = true;
    try {
        const response = await api.getTicket(ticketId);
        // Преобразуем данные в нужный формат
        const ticketData = response.data;
        currentTicket.value = {
            id: ticketData.id,
            chat_id: ticketData.chat_id,
            priority_id: ticketData.priority_id,
            priority: ticketData.priority,
            service: ticketData.service,
            summary: ticketData.summary,
            trace: ticketData.trace,
            back_logs: ticketData.back_logs,
            front_logs: ticketData.front_logs,
            user_id: ticketData.user_id,
            username: ticketData.username,
            email: ticketData.email,
            role_id: ticketData.role_id,
            role: ticketData.role,
            date_of_create: ticketData.date_of_create
        };
        isEditorOpen.value = false;
        isChatSelectionOpen.value = false;
        return true;
    } catch (err) {
        error.value = err.response?.data?.detail || 'Ошибка загрузки тикета';
        return false;
    } finally {
        isLoading.value = false;
    }
}

    const resetCurrentTicket = () => {
        currentTicket.value = null;
        isEditorOpen.value = false;
        isChatSelectionOpen.value = false;
    }

    return {
        tickets,
        currentTicket,
        isLoading,
        error,
        isChatSelectionOpen,
        isEditorOpen,
        fetchTickets,
        openChatSelection,
        openTicketEditor,
        saveTicket,
        resetCurrentTicket,
        openTicketView
    }
})

   
