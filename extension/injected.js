(function () {
  const originalConsoleError = console.error;
  const originalConsoleWarn = console.warn;
  let errorScreenshotTimeout = null;

  window.__logAssistIsLogging = false;
  window.__logAssistHasError = false;

  window.addEventListener("message", (event) => {
    if (event.source !== window) return;

    if (event.data?.type === "log-assist-started") {
      window.__logAssistIsLogging = true;
      window.__logAssistHasError = false;
    } else if (event.data?.type === "log-assist-stopped") {
      window.__logAssistIsLogging = false;
      window.__logAssistHasError = false;
    }
  });
  
  const originalFetch = window.fetch;
  window.fetch = async (...args) => {
    const url = args[0];
    const method = args[1]?.method || "GET";

    try {
      const response = await originalFetch(...args);

      queueMicrotask(async () => {
        if (window.__logAssistIsLogging && response.status >= 400) {
          let errorBody = "";
          let reqId = "";
          try {
            const clone = response.clone();
            errorBody = await clone.text();
            reqId = clone.headers.get("x-request-id") || clone.headers.get("x-req-id") || "";
          } catch (_) {}

          window.postMessage({
            source: 'log-assist',
            type: 'network-error',
            data: {
              url,
              status: response.status,
              method,
              body: errorBody?.substring(0, 500) || '',
              reqId,
              timestamp: new Date().toISOString()
            }
          }, '*');
          captureErrorScreenshot();
        }
      });

      return response;
    } catch (e) {
      queueMicrotask(() => {
        if (window.__logAssistIsLogging) {
          let reqId = "";

          if (e instanceof Response) {
            try {
              reqId = e.headers.get("x-request-id") || e.headers.get("x-req-id") || "";
            } catch (_) {}
          }

          window.postMessage({
            source: 'log-assist',
            type: 'network-error',
            data: {
              url,
              status: "fetch-failed",
              method,
              body: e?.message || '',
              reqId,
              timestamp: new Date().toISOString()
            }
          }, '*');
          captureErrorScreenshot();
        }
      });
      throw e;
    }
  };

  const origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (method, url, ...rest) {
    this.addEventListener("load", function () {
      if (window.__logAssistIsLogging && this.status >= 400) {
        let reqId = "";
        try {
          reqId = this.getResponseHeader("x-request-id") || this.getResponseHeader("x-req-id") || "";
        } catch (_) {}

        window.postMessage({
          source: 'log-assist',
          type: 'network-error',
          data: {
            url,
            status: this.status,
            method,
            body: this.responseText?.substring(0, 500) || '',
            reqId,
            timestamp: new Date().toISOString()
          }
        }, '*');
        captureErrorScreenshot();
      }
    });
    return origOpen.call(this, method, url, ...rest);
  };


  function captureErrorScreenshot() {
    if (window.__logAssistHasError || !window.__logAssistIsLogging) return;
    window.__logAssistHasError = true;
    
    // Защита от слишком частых скриншотов (не чаще чем раз в 5 секунд)
    if (errorScreenshotTimeout) {
      clearTimeout(errorScreenshotTimeout);
    }
    
    errorScreenshotTimeout = setTimeout(() => {
      window.__logAssistHasError = false;
    }, 500);
    
    try {
      window.postMessage({ 
        source: 'log-assist', 
        type: 'error-screenshot-request'
      }, '*');
    } catch (e) {
      console.warn("Не удалось отправить запрос на скриншот:", e);
    }
  }

  // Обработчик ошибок консоли
  console.error = function (...args) {
    const simplifiedArgs = args.map(arg => {
      if (arg instanceof Error) {
        return {
          message: arg.message,
          stack: arg.stack ? arg.stack.split('\n')[0] : undefined
        };
      }
      return typeof arg === 'object' ? JSON.stringify(arg) : arg;
    });
    
    window.postMessage({ 
      source: 'log-assist', 
      type: 'console-error', 
      data: simplifiedArgs.length === 1 ? simplifiedArgs[0] : simplifiedArgs
    }, '*');
    
    captureErrorScreenshot();
    originalConsoleError.apply(console, args);
  };

  console.warn = function (...args) {
    const simplifiedArgs = args.map(arg => {
      if (arg instanceof Error) return arg.message;
      return typeof arg === 'object' ? JSON.stringify(arg) : arg;
    });
    
    window.postMessage({ 
      source: 'log-assist', 
      type: 'console-warn', 
      data: simplifiedArgs.length === 1 ? simplifiedArgs[0] : simplifiedArgs
    }, '*');
    originalConsoleWarn.apply(console, args);
  };

  // Обработчик глобальных ошибок
  window.onerror = function (msg, url, lineNo, columnNo, error) {
    window.postMessage({
      source: 'log-assist',
      type: 'onerror',
      data: {
        message: typeof msg === 'string' ? msg : 'Unknown error',
        source: url,
        line: lineNo,
        column: columnNo,
        stack: error?.stack ? error.stack.split('\n').slice(0, 2).join('\n') : undefined
      }
    }, '*');
    
    captureErrorScreenshot();
  };

  // Обработчик необработанных промисов
  window.addEventListener('unhandledrejection', function (event) {
    const reason = event.reason;
    window.postMessage({
      source: 'log-assist',
      type: 'unhandledrejection',
      data: {
        message: reason instanceof Error ? reason.message : String(reason),
        stack: reason instanceof Error && reason.stack ? reason.stack.split('\n')[0] : undefined
      }
    }, '*');
    
    captureErrorScreenshot();
  });
})();