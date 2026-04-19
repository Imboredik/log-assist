function isExtensionContextValid() {
  try {
    return chrome && chrome.runtime && chrome.runtime.id;
  } catch (e) {
    return false;
  }
}

async function safeSendMessage(message) {
  if (!isExtensionContextValid()) {
    throw new Error("Extension context invalidated");
  }
  
  try {
    return await chrome.runtime.sendMessage(message);
  } catch (error) {
    if (error.message.includes("Extension context invalidated")) {
      setTimeout(() => window.location.reload(), 1000);
    }
    throw error;
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!isExtensionContextValid()) {
    return;
  }

  if (message.action === "ping") {
    sendResponse({ alive: true });
    return true;
  }

  if (message.action === "authCompleted" && message.token) {
    chrome.storage.local.set({ 'assist-log-token': message.token })
      .then(() => {
        sendResponse({ status: "ok" });
        
        const messageElem = document.querySelector("#log-message");
        const startBtn = document.querySelector("#startBtn");
        if (messageElem && startBtn) {
          messageElem.textContent = "Авторизация успешна!";
          startBtn.textContent = "Начать сканирование";
        }
      })
      .catch(error => {
        console.error("Ошибка сохранения токена:", error);
        sendResponse({ status: "error", error: error.message });
      });
    return true;
  }
});

(() => {
    const capturedScreenshots = [];
  const script = document.createElement('script');
  script.src = chrome.runtime.getURL("injected.js");
  script.onload = () => script.remove();
  (document.head || document.documentElement).appendChild(script);

  if (window.location.href.includes('/login')) {
    console.log("Log Assist: content.js отключён на /login");
    return;
  }
  if (document.getElementById("log-assist-panel")) return;

  chrome.runtime.onMessage.addListener((message) => {
    if (message.action === "showLogAssistPanel") {
      if (!document.getElementById("log-assist-panel")) {
        createPanel();
      }
    }
  });

  let isLogging = false;
  let consoleLogs = [];
  let networkLogs = [];
  let panel = null;
  let panelHidden = false;

  window.addEventListener("message", (event) => {
    if (event.source !== window) return;
    if (!event.data || event.data.source !== "log-assist") return;

    if (!isLogging) return;
    
    if (event.data.type?.startsWith("console")) {
      consoleLogs.push({ type: event.data.type, data: event.data.data });
    } else if (event.data.type === "onerror" || event.data.type === "unhandledrejection") {
      consoleLogs.push({ type: event.data.type, data: event.data.data });
    } else if (event.data.type === "network-error") {
      networkLogs.push({
        ...event.data.data,
        type: "network-error"
      });
    }
  });

  window.addEventListener("message", async (event) => {
    if (event.source !== window || event.data?.type !== "error-screenshot-request") return;

    const wasPanelVisible = panel && panel.style.display !== 'none';

    if (panel) {
      panel.style.opacity = '0';
      panel.style.transition = 'opacity 0.15s ease';
    }

    // Скрываем панель
    setTimeout(async () => {
      if (panel) panel.style.display = 'none';
      await new Promise(resolve => setTimeout(resolve, 50));

      const overlay = document.createElement('div');
      overlay.className = 'screenshot-overlay';
      document.body.appendChild(overlay);

      const flash = document.createElement('div');
      flash.className = 'screenshot-flash';
      document.body.appendChild(flash);

      try {
        const resp = await chrome.runtime.sendMessage({ action: "prepareScreenshot" });

        if (resp?.readyForAnimation) {
          overlay.classList.add('active');
          flash.classList.add('active');

          const screenshot = await new Promise((resolve) => {
            chrome.runtime.sendMessage({ action: "getCachedScreenshot" }, (res) => {
              resolve(res?.screenshot);
            });
          });

          if (screenshot) {
            capturedScreenshots.push(screenshot);
          }

          // Завершаем анимацию
          setTimeout(() => {
            flash.classList.remove('active');
            overlay.classList.remove('active');
            setTimeout(() => {
              overlay.remove();
              flash.remove();
              if (panel && wasPanelVisible) {
                panel.style.display = '';
                panel.style.opacity = '1';
              }
            }, 200);
          }, 200);
        }
      } catch (e) {
        console.warn("Ошибка при создании скриншота ошибки:", e);
        overlay.remove();
        flash.remove();
        if (panel && wasPanelVisible) {
          panel.style.display = '';
          panel.style.opacity = '1';
        }
      }
    }, 150);
  });



  function createPanel() {
    panel = document.createElement("div");
    panel.id = "log-assist-panel";
    panel.className = "log-panel";
    panel.innerHTML = `
      <div class="log-header" id="dragHandle">
        <button id="closeBtn">✖</button>
      </div>
      <div class="separator"></div>
      <div class="log-logo">
        <span>Log</span><span>Assist</span>
      </div>
      <div class="log-actions">
        <button id="startBtn">Начать работу</button>
        <div id="cameraBtnWrapper" style="display:none">
          <img id="cameraBtn" src="${chrome.runtime.getURL('camera.png')}" alt="Скриншот" title="Сделать снимок">
        </div>
      </div>
      <div id="log-message" class="log-message">
        Нажмите кнопку чтобы начать запись логов
      </div>
    `;
    document.body.appendChild(panel);
    setupPanelEvents();
  }

  function setupPanelEvents() {
    const startBtn = panel.querySelector("#startBtn");
    const closeBtn = panel.querySelector("#closeBtn");
    const message = panel.querySelector("#log-message");
    const cameraBtn = panel.querySelector("#cameraBtn");
    const cameraBtnWrapper = panel.querySelector("#cameraBtnWrapper");
    const dragHandle = panel.querySelector("#dragHandle");

    cameraBtn.onclick = async () => {
      if (!window.__logAssistIsLogging) return;

      cameraBtn.classList.add("loading");
      cameraBtn.src = chrome.runtime.getURL("loading.png");

      window.postMessage({ type: "error-screenshot-request" }, "*");

      setTimeout(() => {
        cameraBtn.classList.remove("loading");
        cameraBtn.src = chrome.runtime.getURL("camera.png");
      }, 1500);
    };


    startBtn.onclick = async () => {
      if (!isExtensionContextValid()) {
        showUserError(message, "Ошибка: расширение неактивно. Обновите страницу.");
        return;
      }

      try {
        const result = await chrome.storage.local.get(['assist-log-token']);
        const token = result['assist-log-token'];

        if (token) {
          const isValid = await safeSendMessage({
            action: "validateToken",
            token
          });

          if (isValid) {
            toggleLogging(startBtn, message);
            return;
          }
        }

        message.textContent = "Перенаправляем на страницу логина...";
        const authResponse = await safeSendMessage({ action: "requestAuth" });

        if (authResponse?.error) {
          throw new Error(authResponse.error);
        }

        const tokenReady = await waitForTokenWithStatus(message, 10000, 30);

        if (tokenReady) {
          message.textContent = "Авторизация успешна!";
          startBtn.textContent = "Начать сканирование";
        } else {
          showUserError(message, "Ошибка аутентификации, попробуйте снова");
        }
      } catch (error) {
        console.error("Ошибка авторизации:", error);
        showUserError(message, "Ошибка аутентификации, попробуйте снова");
        if (error.message.includes("Extension context invalidated")) {
          setTimeout(() => window.location.reload(), 2000);
        }
      }
    };

    closeBtn.onclick = () => {
      panel.remove();
      panel = null;
    };

    let isDragging = false;
    let offsetX = 0;
    let offsetY = 0;

    dragHandle.addEventListener("mousedown", (e) => {
      isDragging = true;
      offsetX = e.clientX - panel.getBoundingClientRect().left;
      offsetY = e.clientY - panel.getBoundingClientRect().top;
      document.body.style.userSelect = "none";
    });

    document.addEventListener("mousemove", (e) => {
      if (isDragging && panel) {
        panel.style.left = `${e.clientX - offsetX}px`;
        panel.style.top = `${e.clientY - offsetY}px`;
        panel.style.right = "auto";
        panel.style.bottom = "auto";
      }
    });

    document.addEventListener("mouseup", () => {
      isDragging = false;
      document.body.style.userSelect = "";
    });
  }

  function showUserError(messageElem, text) {
    messageElem.textContent = text;
  }

  function toggleLogging(startBtn, message) {
    if (isLogging) {
      startBtn.disabled = true;
      startBtn.textContent = "Остановка...";
      stopLogging(startBtn, message);
    } else {
      startBtn.disabled = true;
      startBtn.textContent = "Подготовка...";
      startLogging(startBtn, message);
    }
  }

  function startLogging(startBtn, message) {
    cameraBtnWrapper.style.display = 'flex';
    consoleLogs = [];
    networkLogs = [];

    const originalConsole = {
      log: console.log,
      error: console.error,
      warn: console.warn,
      info: console.info
    };

    window._logAssistCleanup = () => {
      Object.keys(originalConsole).forEach(key => {
        console[key] = originalConsole[key];
      });
    };

    setTimeout(() => {
      startBtn.disabled = false;
      startBtn.textContent = "Закончить сканирование";
      message.textContent = "Сделайте действия, от которых у вас произошла ошибка";
      window.__logAssistIsLogging = true;
      window.postMessage({ type: "log-assist-started" }, "*");
      isLogging = true;
    }, 300);
  }

  function stopLogging(startBtn, message) {
    startBtn.disabled = true;
    cameraBtnWrapper.style.display = 'none';
    startBtn.textContent = "Отправка данных...";
    message.textContent = "Сканирование завершено. Отправляем данные...";

    if (window._logAssistCleanup) {
      window._logAssistCleanup();
      delete window._logAssistCleanup;
    }


    const compressedLogs = [...consoleLogs, ...networkLogs];
    const wasPanelVisible = panel && panel.style.display !== 'none';
    
    // Сначала делаем панель прозрачной
    if (panel) {
      panel.style.opacity = '0';
      panel.style.transition = 'opacity 0.3s ease';
    }

    // Ждем завершения анимации прозрачности
    setTimeout(async () => {
      // Полностью скрываем панель
      if (panel) {
        panel.style.display = 'none';
      }

      // Даем время браузеру для рендеринга страницы без панели
      await new Promise(resolve => setTimeout(resolve, 100));

      // Быстрая анимация ошибки
      const overlay = document.createElement('div');
      overlay.className = 'screenshot-overlay';
      document.body.appendChild(overlay);

      const flash = document.createElement('div');
      flash.className = 'screenshot-flash';
      document.body.appendChild(flash);

      // Отправляем запрос на скриншот и ждем его завершения
      try {
        const response = await chrome.runtime.sendMessage({
          action: "prepareScreenshot",
          logs: compressedLogs
        });

        if (response?.readyForAnimation) {
          // Только после подтверждения, что скриншот сделан, запускаем анимацию
          overlay.classList.add('active');
          flash.classList.add('active');

          const sendPromise = chrome.runtime.sendMessage({
            action: "sendDataToServer",
            logs: compressedLogs,
            screenshots: capturedScreenshots
          }).catch(error => {
            console.error("Ошибка при отправке:", error);
            return { error: error.message };
          });


          setTimeout(() => {
            flash.classList.remove('active');
            overlay.classList.remove('active');

            setTimeout(() => {
              overlay.remove();
              flash.remove();

              if (panel && wasPanelVisible) {
                panel.style.display = '';
                panel.style.opacity = '1';
              }

              sendPromise.then(response => {
                consoleLogs = [];
                networkLogs = [];
                capturedScreenshots.length = 0;
                if (window._logAssistCleanup) {
                  window._logAssistCleanup();
                  delete window._logAssistCleanup;
                }
                if (response?.chatId) {
                  message.textContent = `Открываем чат #${response.chatId}...`;
                  message.style.color = "green";
                  redirectAndClosePanel(response.chatId);
                } else if (response?.error) {
                  console.error("Ошибка отправки данных:", response.error);
                  showUserError(message, "Ошибка на сервере, попробуйте снова");
                }

                startBtn.disabled = false;
                startBtn.textContent = "Начать работу";
                isLogging = false;
              });
            }, 200);
          }, 200);

        }
      } catch (error) {
        console.error("Ошибка при создании скриншота:", error);
        overlay.remove();
        flash.remove();
        if (panel && wasPanelVisible) {
          panel.style.display = '';
          panel.style.opacity = '1';
        }
        showUserError(message, "Ошибка при создании скриншота");
        startBtn.disabled = false;
        startBtn.textContent = "Начать работу";
        isLogging = false;
      }
    }, 300);
  }

  function redirectAndClosePanel(chatId) {
    chrome.runtime.sendMessage({
      action: "openChatTab",
      chatId
    }).then(() => {
      if (panel) {
        panel.remove();
        panel = null;
      }
      
      window.postMessage({ type: "log-assist-stopped" }, "*");
      window.__logAssistIsLogging = false;
      window.__logAssistHasError = false;

      
      if (window._logAssistCleanup) {
        window._logAssistCleanup();
        delete window._logAssistCleanup;
      }
    });
  }
})();

async function waitForTokenWithStatus(messageElem, interval = 500, maxAttempts = 120) {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const result = await chrome.storage.local.get(['assist-log-token']);
    const token = result['assist-log-token'];

    messageElem.textContent = `Ожидание токена... Попытка ${attempt} из ${maxAttempts}`;

    if (token) {
      const isValid = await chrome.runtime.sendMessage({
        action: "validateToken",
        token
      });
      
      if (isValid) {
        messageElem.textContent = "Авторизация успешна!";
        return true;
      }
    }

    await new Promise(res => setTimeout(res, interval));
  }
  
  return false;
}

async function waitForTokenWithRetry(messageElem, maxAttempts = 60, interval = 5000) {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const result = await chrome.storage.local.get(['assist-log-token']);
      const token = result['assist-log-token'];

      messageElem.textContent = `Ожидание токена... (${attempt}/${maxAttempts})`;

      if (token) {
        const isValid = await safeSendMessage({
          action: "validateToken",
          token
        });
        
        if (isValid) {
          messageElem.textContent = "Авторизация успешна!";
          return true;
        }
      }

      await new Promise(res => setTimeout(res, interval));
    } catch (error) {
      console.error(`Ошибка при проверке токена (попытка ${attempt}):`, error);
      if (error.message.includes("Extension context invalidated")) {
        setTimeout(() => window.location.reload(), 2000);
        return false;
      }
    }
  }
  
  return false;
}

