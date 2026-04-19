function isExtensionContextValid() {
  try {
    return typeof chrome !== 'undefined' && 
           chrome.runtime && 
           chrome.runtime.id && 
           chrome.runtime.sendMessage;
  } catch (e) {
    return false;
  }
}

window.addEventListener("message", async (event) => {
  if (event.source !== window) return;
  if (event.data?.type !== "ASSIST_LOG_AUTH") return;

  const { token, sourceTabId } = event.data;
  console.log("Контент-скрипт получил токен", token);

  if (!token || !sourceTabId) {
    console.error("Invalid token or sourceTabId");
    return;
  }

  if (!isExtensionContextValid()) {
    console.error("Extension context invalidated");
    return;
  }

  try {
    // Подтверждение получения
    event.source.postMessage({
      type: "ASSIST_LOG_AUTH_ACK",
      received: true
    }, event.origin);

    let tokenSent = false;
    
    // Функция для отправки токена с повторными попытками
    const sendTokenWithRetry = async (method, maxAttempts = 3) => {
      for (let attempt = 0; attempt < maxAttempts; attempt++) {
        try {
          if (method === 'runtime') {
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
          } else if (method === 'port') {
            const port = chrome.runtime.connect({ name: "auth-port" });
            port.postMessage({
              type: "ASSIST_LOG_AUTH",
              token,
              sourceTabId
            });
            await new Promise(resolve => setTimeout(resolve, 100));
            port.disconnect();
            return true;
          }
        } catch (e) {
          console.error(`Attempt ${attempt + 1} failed for method ${method}:`, e);
          if (attempt < maxAttempts - 1) {
            await new Promise(resolve => setTimeout(resolve, 300));
          }
        }
      }
      return false;
    };

    // Пробуем разные методы с повторными попытками
    tokenSent = await sendTokenWithRetry('runtime') || 
                await sendTokenWithRetry('port') || 
                false;

    // Последняя попытка через postMessage
    if (!tokenSent) {
      window.postMessage({
        type: "ASSIST_LOG_AUTH_FALLBACK",
        token,
        sourceTabId
      }, "*");
      console.log("Token sent via fallback postMessage");
    }

  } catch (error) {
    console.error("Error in auth message handler:", error);
  } finally {
    // Даем время на отправку токена перед закрытием
    setTimeout(() => {
      window.close();
    }, 300);
  }
});