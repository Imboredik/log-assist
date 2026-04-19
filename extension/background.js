let authRequest = null;
let isCaptureRunning = false;
let cachedLogs = null;
let cachedScreenshot = null;

function isExtensionContextValid() {
  try {
    return chrome && chrome.runtime && chrome.runtime.id;
  } catch (e) {
    return false;
  }
}

async function safeSendMessage(tabId, message) {
  if (!isExtensionContextValid()) {
    throw new Error("Extension context invalidated");
  }
  
  try {
    return await chrome.tabs.sendMessage(tabId, message);
  } catch (error) {
    if (error.message.includes("Extension context invalidated")) {
      throw error;
    }
    console.warn("Message sending error:", error);
    return null;
  }
}

chrome.runtime.onConnect.addListener((port) => {
  if (!isExtensionContextValid()) return;
  
  if (port.name === "auth-port") {
    console.log("Auth port connected");
    port.onMessage.addListener((msg) => {
      if (msg.type === "ASSIST_LOG_AUTH") {
        handleAuthSuccess({
          token: msg.token,
          sourceTabId: msg.sourceTabId
        }, { tab: { id: parseInt(msg.sourceTabId) } });
      }
    });
    port.onDisconnect.addListener(() => {
      console.log("Auth port disconnected");
    });
  }
});

function openLoginPage(tab) {
  return new Promise((resolve) => {
    if (!isExtensionContextValid()) {
      resolve(null);
      return;
    }

    chrome.tabs.create({
      url: `http://localhost:5173/login?extension=true&sourceTabId=${tab.id}`,
      active: true
    }, (loginTab) => {
      const tabId = loginTab.id;
      let resolved = false;

      // Увеличиваем таймаут до 5 минут (300000 мс)
      const timeoutId = setTimeout(() => {
        if (!resolved) {
          cleanup();
          resolve(null);
        }
      }, 300000);

      const cleanup = () => {
        resolved = true;
        chrome.runtime.onMessage.removeListener(onMessageListener);
        chrome.tabs.onRemoved.removeListener(onRemovedListener);
        clearTimeout(timeoutId);
      };

      const onMessageListener = (message, sender, sendResponse) => {
        if (sender.tab?.id === tabId && message.action === "authSuccess") {
          if (!resolved) {
            cleanup();
            resolve(message.token);
          }
          sendResponse({ status: "success" });
          return true;
        }
      };

      const onRemovedListener = (removedTabId) => {
        if (removedTabId === tabId && !resolved) {
          cleanup();
          resolve(null);
        }
      };

      chrome.runtime.onMessage.addListener(onMessageListener);
      chrome.tabs.onRemoved.addListener(onRemovedListener);

      if (!isExtensionContextValid()) {
        cleanup();
        resolve(null);
        return;
      }

      // Добавляем повторные попытки вставки скрипта
      const injectScript = async (attempt = 0) => {
        try {
          await chrome.scripting.executeScript({
            target: { tabId },
            files: ['inject-auth.js']
          });
        } catch (error) {
          console.error(`Ошибка вставки inject-auth.js (попытка ${attempt + 1}):`, error);
          if (attempt < 2) { // 3 попытки с задержкой
            await new Promise(resolve => setTimeout(resolve, 500));
            return injectScript(attempt + 1);
          }
          if (!resolved) {
            cleanup();
            resolve(null);
          }
        }
      };

      // Даем странице время загрузиться перед вставкой скрипта
      setTimeout(() => {
        injectScript().catch(e => {
          console.error("Ошибка при вставке скрипта:", e);
          if (!resolved) {
            cleanup();
            resolve(null);
          }
        });
      }, 1000);
    });
  });
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!isExtensionContextValid()) {
    sendResponse({ error: "Extension context invalidated" });
    return false;
  }

  switch (message.action) {
    case "validateToken": {
      const valid = validateToken(message.token);
      sendResponse(valid);
      return true;
    }

    case "requestAuth":
      (async () => {
        try {
          if (authRequest) {
            const token = await authRequest;
            sendResponse(token ? { token } : { error: "Auth failed" });
          } else {
            authRequest = openLoginPage(sender.tab);
            const token = await authRequest;
            sendResponse(token ? { token } : { error: "Auth failed" });
            authRequest = null;
          }
        } catch (error) {
          console.error("Ошибка логина:", error);
          sendResponse({ error: error.message });
          authRequest = null;
        }
      })();
      return true;

    case "authSuccess":
      (async () => {
        try {
          await handleAuthSuccess(message, sender);
          sendResponse({ status: "received" });
        } catch (error) {
          console.error("authSuccess error:", error);
          sendResponse({ error: error.message });
        }
      })();
      return true;

    case "captureAndSend":
      (async () => {
        try {
          const result = await captureAndSendData(message, sender.tab?.id);
          sendResponse(result);
        } catch (err) {
          console.error("Ошибка captureAndSend:", err);
          sendResponse({ error: err.message });
        }
      })();
      return true;

    case "getCachedScreenshot":
      sendResponse({ screenshot: cachedScreenshot });
      return true;

    case "prepareScreenshot":
      (async () => {
        try {
          // Сначала делаем скриншот
          const screenshotDataUrl = await chrome.tabs.captureVisibleTab(undefined, { 
            format: "jpeg", 
            quality: 80
          });
          cachedScreenshot = screenshotDataUrl;
          
          // Подтверждаем, что скриншот готов
          sendResponse({ readyForAnimation: true });
        } catch (error) {
          console.error("Ошибка при создании скриншота:", error);
          sendResponse({ error: error.message });
        }
      })();
      return true;

    case "sendDataToServer":
      (async () => {
        try {
          // Используем уже сделанный скриншот
          const result = await captureAndSendData({
            logs: message.logs,
            screenshots: message.screenshots && message.screenshots.length > 0 ? message.screenshots : [cachedScreenshot]
          }, sender.tab?.id);
          sendResponse(result);
        } catch (err) {
          console.error("Ошибка отправки данных:", err);
          sendResponse({ error: err.message });
        }
      })();
      return true;

    case "openChatTab":
      (async () => {
        try {
          if (message.chatId) {
            await chrome.tabs.create({
              url: `http://localhost:5173/chat?chat_id=${encodeURIComponent(message.chatId)}`,
              active: true
            });
          }
          sendResponse({ status: "ok" });
        } catch (error) {
          sendResponse({ error: error.message });
        }
      })();
      return true;

    default:
      sendResponse({ error: "Unknown action" });
      return false;
  }
});


chrome.action.onClicked.addListener(async (tab) => {
  if (!isExtensionContextValid()) return;
  
  try {
    await chrome.scripting.insertCSS({ target: { tabId: tab.id }, files: ["panel.css"] });
    await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["content.js"] });
    console.log('Extension initialized for tab:', tab.id);
  } catch (error) {
    console.error('Extension initialization failed:', error);
  }
});

function validateToken(token) {
  if (!token || typeof token !== 'string') return false;
  const parts = token.split('.');
  if (parts.length !== 3) return false;

  try {
    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);
    return payload.exp && now < payload.exp;
  } catch {
    return false;
  }
}

async function isContentScriptReady(tabId) {
  try {
    const response = await chrome.tabs.sendMessage(tabId, { action: "ping" });
    return !!response;
  } catch (error) {
    console.warn("Content script не готов:", error);
    return false;
  }
}

async function handleAuthSuccess(message, sender) {
  const token = message.token;
  const sourceTabId = parseInt(message.sourceTabId);

  if (!token || !sourceTabId || isNaN(sourceTabId)) {
    console.error("Invalid token or sourceTabId");
    return;
  }

  try {
    // Сохраняем токен в local storage
    await chrome.storage.local.set({ 'assist-log-token': token });

    // Проверяем токен
    const userInfo = await fetch('http://localhost:5173/api/v1/user', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!userInfo.ok) {
      throw new Error("Невалидный токен");
    }

    // Активируем исходную вкладку
    await chrome.tabs.update(sourceTabId, { active: true });

    // Ждём, чтобы браузер точно переключил вкладку
    await new Promise(resolve => setTimeout(resolve, 300));

    // Передаём токен в content.js
    await chrome.tabs.sendMessage(sourceTabId, {
      action: "authCompleted",
      token
    });

    // Ещё немного подождём, чтобы content.js успел отреагировать
    await new Promise(resolve => setTimeout(resolve, 300));

    // Закрываем вкладки логина
    const loginTabs = await chrome.tabs.query({ url: "http://localhost:5173/login*" });
    await Promise.all(loginTabs.map(tab => chrome.tabs.remove(tab.id)));

  } catch (error) {
    console.error("Error in handleAuthSuccess:", error);
    await chrome.storage.local.remove(['assist-log-token']);
  }
}


async function captureAndSendData(message, incomingTabId) {
  const { 'assist-log-token': token } = await chrome.storage.local.get(['assist-log-token']);
  if (!token) {
    throw new Error("Требуется авторизация. Пожалуйста, войдите в систему.");
  }

  let tabId = incomingTabId;
  if (!tabId) {
    const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
    tabId = activeTab?.id;
  }
  if (!tabId) throw new Error("Не удалось определить вкладку.");

  const maxAttempts = 3;
  let lastError = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const logs = Array.isArray(message.logs)
        ? message.logs
        : Object.entries(message.logs || {}).map(([type, data]) => ({ type, data }));

      const payload = {
        message: "Составь краткое резюме (До 1000 слов, 3-4 абзаца) о проблеме проанализировав изображения и логи, определи систему, в которой возникла проблема и составь название чата, отражающее его содержание, длиной не более 20 символов. Ответ заключи в XML:<chat_name>Название чата</chat_name>(Название чата не больше 20 символов)<service>Сервис в котором возникла проблема</service><summary>Краткое резюме о проблеме</summary>. Ответ должен быть полностью на русском языке.",
        back_logs: "", 
        front_logs: JSON.stringify(logs),
        images: Array.isArray(message.screenshots) && message.screenshots.length > 0 ? message.screenshots : (message.screenshot ? [message.screenshot] : [])
      };
      
      console.log("Отправляемый запрос на сервер:", {
        message: payload.message.substring(0, 200) + "...",
        back_logs: payload.back_logs,
        front_logs: payload.front_logs ? payload.front_logs.substring(0, 200) + "..." : "null",
        images_count: payload.images ? payload.images.length : 0
      });

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);

      try {
        const response = await fetch('http://localhost:5173/api/v1/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(payload),
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          let errorText = await response.text();
          try {
            const errorData = JSON.parse(errorText);
            errorText = errorData.detail || errorText;
          } catch {}
          
          if (response.status === 502 && attempt < maxAttempts) {
            lastError = new Error(`Сервер временно недоступен (502). Попытка ${attempt} из ${maxAttempts}`);
            await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
            continue;
          }
          
          throw new Error(errorText);
        }

        const data = await response.json();
        
        if (Array.isArray(data) && data.length === 2) {
          cachedLogs = null;
          cachedScreenshot = null;
          
          return { 
            status: "success", 
            chatId: data[0].id,
            message: data[1].content
          };
        }
        
        throw new Error("Неожиданный формат ответа от сервера");
        
      } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
          throw new Error("Сервер не ответил за 2 минуты. Попробуйте позже.");
        }
        
        if (error.message.includes("401") || error.message.includes("Не авторизован")) {
          await chrome.storage.local.remove(['assist-log-token']);
          throw new Error("Сессия истекла. Пожалуйста, войдите снова.");
        }
        
        throw error;
      }
    } catch (error) {
      lastError = error;
      if (attempt < maxAttempts) {
        console.warn(`Попытка ${attempt} не удалась, пробуем снова...`, error);
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
      } else {
        cachedLogs = null;
        cachedScreenshot = null;
        throw lastError;
      }
    }
  }
}

chrome.action.onClicked.addListener(async (tab) => {
  if (!isExtensionContextValid()) return;

  try {
    await chrome.scripting.insertCSS({ target: { tabId: tab.id }, files: ["panel.css"] });
    await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["content.js"] });

    await chrome.tabs.sendMessage(tab.id, { action: "showLogAssistPanel" });

    console.log('Log Assist panel requested for tab:', tab.id);
  } catch (error) {
    console.error('Extension initialization failed:', error);
  }
});
