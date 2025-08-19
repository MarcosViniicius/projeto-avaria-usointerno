// Scanner de código de barras ultra-compatível
(function () {
  "use strict";

  // Variáveis globais
  var scanBtn, scannerContainer, codigoInput, nomeInput;
  var codeReader,
    videoElement,
    isScanning = false,
    stream;
  var scannerMethod = "none";
  var retryCount = 0;
  var maxRetries = 3;

  // Inicialização quando documento carrega
  function init() {
    scanBtn = document.getElementById("scan-btn");
    scannerContainer = document.getElementById("scanner-container");
    codigoInput = document.getElementById("codigo_barras");
    nomeInput = document.getElementById("nome_produto");

    if (scanBtn) {
      scanBtn.addEventListener("click", handleScanClick);
    }

    // Detectar capacidades do dispositivo
    detectCapabilities();
  }

  // Detectar capacidades do navegador/dispositivo
  function detectCapabilities() {
    var info = {
      mobile:
        /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
          navigator.userAgent
        ),
      iOS: /iPad|iPhone|iPod/.test(navigator.userAgent),
      android: /Android/i.test(navigator.userAgent),
      chrome: /Chrome/i.test(navigator.userAgent),
      firefox: /Firefox/i.test(navigator.userAgent),
      safari:
        /Safari/i.test(navigator.userAgent) &&
        !/Chrome/i.test(navigator.userAgent),
      modernCamera: !!(
        navigator.mediaDevices && navigator.mediaDevices.getUserMedia
      ),
      legacyCamera: !!(
        navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia ||
        navigator.msGetUserMedia
      ),
      // Verificação mais robusta para localhost, IPs privados e ambientes seguros
      https:
        window.location.protocol === "https:" ||
        window.location.hostname === "localhost" ||
        window.location.hostname === "127.0.0.1" ||
        window.location.hostname.indexOf("localhost") !== -1 ||
        window.location.hostname.indexOf("127.0.0.1") !== -1 ||
        window.location.port === "5000" ||
        // Aceitar IPs privados da rede local
        window.location.hostname.match(/^192\.168\./) ||
        window.location.hostname.match(/^10\./) ||
        window.location.hostname.match(/^172\.(1[6-9]|2[0-9]|3[0-1])\./) ||
        // Aceitar qualquer IP local com porta 5000 (Flask dev server)
        window.location.port === "5000" ||
        window.location.href.indexOf(":5000") !== -1 ||
        window.location.href.indexOf("localhost") !== -1,
    };

    // Forçar modo camera para localhost mesmo sem HTTPS
    var isLocalhost =
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1" ||
      window.location.hostname.indexOf("localhost") !== -1 ||
      window.location.port === "5000";

    // Determinar melhor método de scanner
    if (
      (info.https || isLocalhost) &&
      (info.modernCamera || info.legacyCamera)
    ) {
      scannerMethod = info.modernCamera ? "modern" : "legacy";
    } else if (info.modernCamera || info.legacyCamera) {
      // Tentar mesmo sem HTTPS em alguns casos
      scannerMethod = info.modernCamera ? "modern" : "legacy";
    } else {
      scannerMethod = "manual";
    }

    // Log de debug mais detalhado
    console.log("=== DIAGNÓSTICO DO SCANNER ===");
    console.log("URL atual:", window.location.href);
    console.log("Protocolo:", window.location.protocol);
    console.log("Hostname:", window.location.hostname);
    console.log("Porta:", window.location.port);
    console.log("É localhost?", isLocalhost);
    console.log("Capacidades detectadas:", info);
    console.log("Método de scanner escolhido:", scannerMethod);
    console.log("==============================");
  }

  function handleScanClick() {
    if (isScanning) {
      stopScanning();
      return;
    }

    switch (scannerMethod) {
      case "modern":
      case "legacy":
        startCameraScanner();
        break;
      case "manual":
      default:
        showManualInput();
        break;
    }
  }

  function startCameraScanner() {
    try {
      showLoadingState();

      // Setup video element
      videoElement = document.createElement("video");
      videoElement.setAttribute("autoplay", "true");
      videoElement.setAttribute("playsinline", "true");
      videoElement.setAttribute("muted", "true");
      videoElement.style.width = "100%";
      videoElement.style.maxWidth = "400px";
      videoElement.style.height = "300px";
      videoElement.style.border = "2px solid #007bff";
      videoElement.style.borderRadius = "8px";

      // Configurações de câmera progressivamente mais simples
      var constraintSets = [
        // Configuração ideal
        {
          video: {
            width: { ideal: 640, max: 1280 },
            height: { ideal: 480, max: 720 },
            facingMode: { ideal: "environment" },
            frameRate: { ideal: 15, max: 30 },
          },
        },
        // Configuração média
        {
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: "environment",
          },
        },
        // Configuração básica
        {
          video: {
            facingMode: "environment",
          },
        },
        // Configuração mínima
        {
          video: true,
        },
      ];

      tryConstraints(constraintSets, 0);
    } catch (err) {
      console.error("Erro ao iniciar scanner:", err);
      handleError(err);
    }
  }

  function tryConstraints(constraintSets, index) {
    if (index >= constraintSets.length) {
      showManualInput();
      return;
    }

    var constraints = constraintSets[index];
    console.log("Tentando constraints:", constraints);

    if (scannerMethod === "modern") {
      navigator.mediaDevices
        .getUserMedia(constraints)
        .then(function (mediaStream) {
          setupVideoStream(mediaStream);
        })
        .catch(function (err) {
          console.log("Falha com constraints", index, ":", err);
          tryConstraints(constraintSets, index + 1);
        });
    } else {
      // Legacy getUserMedia
      var getUserMedia =
        navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia ||
        navigator.msGetUserMedia;

      getUserMedia.call(
        navigator,
        constraints,
        function (mediaStream) {
          setupVideoStream(mediaStream);
        },
        function (err) {
          console.log("Falha com constraints", index, ":", err);
          tryConstraints(constraintSets, index + 1);
        }
      );
    }
  }

  function setupVideoStream(mediaStream) {
    stream = mediaStream;

    // Compatibilidade com diferentes navegadores
    if (videoElement.mozSrcObject !== undefined) {
      videoElement.mozSrcObject = stream;
    } else if (videoElement.srcObject !== undefined) {
      videoElement.srcObject = stream;
    } else if (window.URL && window.URL.createObjectURL) {
      videoElement.src = window.URL.createObjectURL(stream);
    } else {
      videoElement.src = stream;
    }

    videoElement.onloadedmetadata = function () {
      var playPromise = videoElement.play();

      if (playPromise !== undefined) {
        playPromise
          .then(function () {
            showVideoAndInitScanner();
          })
          .catch(function (err) {
            console.log("Erro ao reproduzir vídeo:", err);
            showVideoAndInitScanner(); // Tentar mesmo assim
          });
      } else {
        showVideoAndInitScanner();
      }
    };

    videoElement.onerror = function (err) {
      console.error("Erro no vídeo:", err);
      retryOrFallback();
    };
  }

  function showVideoAndInitScanner() {
    scannerContainer.innerHTML = "";
    scannerContainer.appendChild(videoElement);

    // Instruções
    var instructions = document.createElement("div");
    instructions.className = "text-center mt-2";
    instructions.innerHTML =
      '<small class="text-muted">' +
      "📱 Aponte para o código de barras<br>" +
      "Mantenha 10-20cm de distância" +
      "</small>";
    scannerContainer.appendChild(instructions);

    initializeScanner();
  }

  function initializeScanner() {
    // Múltiplas tentativas de inicialização do ZXing
    var zxingMethods = [
      function () {
        return new ZXing.BrowserBarcodeReader();
      },
      function () {
        return new ZXing.BrowserMultiFormatReader();
      },
      function () {
        return new ZXing.BrowserCodeReader();
      },
      function () {
        return new ZXing.BarcodeReader();
      },
    ];

    for (var i = 0; i < zxingMethods.length; i++) {
      try {
        codeReader = zxingMethods[i]();
        break;
      } catch (e) {
        console.log("Falha ao inicializar ZXing método", i, ":", e);
      }
    }

    if (!codeReader) {
      console.error("Nenhum método ZXing funcionou");
      startManualScanner();
      return;
    }

    isScanning = true;
    scanBtn.textContent = "⏹️ Parar Scanner";

    startDecoding();
  }

  function startDecoding() {
    if (!isScanning || !videoElement || !codeReader) return;

    var decodeMethods = [
      function () {
        return codeReader.decodeOnceFromVideoElement(videoElement);
      },
      function () {
        return codeReader.decodeFromVideoElement(videoElement);
      },
      function () {
        return codeReader.decode(videoElement);
      },
    ];

    function tryDecode(methodIndex) {
      if (methodIndex >= decodeMethods.length) {
        // Tentar novamente após delay
        if (isScanning) {
          setTimeout(function () {
            tryDecode(0);
          }, 200);
        }
        return;
      }

      try {
        var decodePromise = decodeMethods[methodIndex]();

        if (decodePromise && decodePromise.then) {
          decodePromise
            .then(function (result) {
              if (result && result.text) {
                handleSuccessfulScan(result.text.trim());
              } else {
                if (isScanning) {
                  setTimeout(function () {
                    tryDecode(0);
                  }, 100);
                }
              }
            })
            .catch(function (err) {
              tryDecode(methodIndex + 1);
            });
        } else {
          tryDecode(methodIndex + 1);
        }
      } catch (err) {
        tryDecode(methodIndex + 1);
      }
    }

    tryDecode(0);
  }

  function handleSuccessfulScan(codigo) {
    if (codigo && codigo.length > 0) {
      codigoInput.value = codigo;
      stopScanning();

      // Feedback
      if (navigator.vibrate) {
        navigator.vibrate([200, 100, 200]);
      }

      showSuccessMessage("✅ Código escaneado: " + codigo);

      // Focar no próximo campo
      if (nomeInput) {
        nomeInput.focus();
      }
    }
  }

  function showSuccessMessage(message) {
    var successDiv = document.createElement("div");
    successDiv.className = "alert alert-success mt-2";
    successDiv.innerHTML = message;
    scannerContainer.appendChild(successDiv);

    setTimeout(function () {
      if (successDiv && successDiv.parentNode) {
        successDiv.parentNode.removeChild(successDiv);
      }
    }, 4000);
  }

  function startManualScanner() {
    // Scanner manual com canvas (para casos extremos)
    if (!videoElement) return;

    var canvas = document.createElement("canvas");
    var ctx = canvas.getContext("2d");
    canvas.width = videoElement.videoWidth || 640;
    canvas.height = videoElement.videoHeight || 480;

    function captureFrame() {
      if (!isScanning) return;

      try {
        ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        var imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

        // Tentar decodificar da imagem
        if (codeReader && codeReader.decodeFromImageData) {
          codeReader
            .decodeFromImageData(imageData)
            .then(function (result) {
              if (result && result.text) {
                handleSuccessfulScan(result.text.trim());
              } else {
                setTimeout(captureFrame, 300);
              }
            })
            .catch(function () {
              setTimeout(captureFrame, 300);
            });
        } else {
          setTimeout(captureFrame, 500);
        }
      } catch (err) {
        setTimeout(captureFrame, 500);
      }
    }

    captureFrame();
  }

  function retryOrFallback() {
    retryCount++;
    if (retryCount < maxRetries) {
      console.log("Tentativa", retryCount, "de", maxRetries);
      setTimeout(function () {
        startCameraScanner();
      }, 1000);
    } else {
      showManualInput();
    }
  }

  function showLoadingState() {
    scannerContainer.innerHTML =
      '<div class="text-center p-3">' +
      '<div class="spinner-border text-primary" role="status">' +
      '<span class="visually-hidden">Carregando...</span>' +
      "</div>" +
      '<p class="mt-2">Iniciando scanner...</p>' +
      "</div>";
  }

  function showManualInput() {
    var currentUrl = window.location.href;
    var isLocalhost =
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1" ||
      window.location.hostname.indexOf("localhost") !== -1;

    var html =
      '<div class="alert alert-info">' +
      "<h6><strong>📱 Informações do Scanner</strong></h6>" +
      "<p><strong>URL atual:</strong> <code>" +
      currentUrl +
      "</code></p>";

    if (isLocalhost) {
      html +=
        "<p><strong>✅ Localhost detectado!</strong> O scanner deveria funcionar.</p>";

      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        html += "<p><strong>✅ API moderna de câmera disponível</strong></p>";
      } else if (
        navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia
      ) {
        html += "<p><strong>⚠️ Usando API legada de câmera</strong></p>";
      } else {
        html += "<p><strong>❌ Nenhuma API de câmera disponível</strong></p>";
      }

      html +=
        '<button class="btn btn-warning btn-sm mt-2" onclick="testCameraAccess()">🔧 Testar Acesso à Câmera</button>';
    } else {
      html +=
        "<p><strong>⚠️ Não é localhost</strong> - Para melhor compatibilidade, use HTTPS ou localhost</p>";
    }

    html +=
      "</div>" +
      '<div class="alert alert-secondary">' +
      "<strong>Alternativas:</strong>" +
      "<ol>" +
      "<li>Digite o código manualmente no campo acima</li>" +
      "<li>Use um app de código de barras e digite o resultado</li>" +
      "<li>Tire uma foto do código e digite</li>" +
      "</ol>" +
      "</div>";

    if (scannerMethod === "manual") {
      html +=
        '<div class="alert alert-warning">' +
        "<small><strong>Dica:</strong> Para usar o scanner automático, acesse via HTTPS.</small>" +
        "</div>";
    }

    scannerContainer.innerHTML = html;
    if (codigoInput) {
      codigoInput.focus();
    }
  }

  // Função global para testar câmera
  window.testCameraAccess = function () {
    console.log("=== TESTE DE ACESSO À CÂMERA ===");
    console.log("URL atual:", window.location.href);
    console.log("Protocolo:", window.location.protocol);
    console.log("Hostname:", window.location.hostname);
    console.log("Porta:", window.location.port);

    var capabilities = detectCapabilities();
    console.log("Capacidades detectadas:", capabilities);

    // Verificar contexto de segurança
    var isSecureContext = capabilities.https;
    console.log("Contexto seguro:", isSecureContext);

    if (!isSecureContext) {
      console.log("⚠️ ATENÇÃO: Contexto não-HTTPS detectado!");
      console.log(
        "Para IPs da rede local (ex: 192.168.x.x), alguns navegadores podem bloquear a câmera."
      );
      console.log("Soluções:");
      console.log("1. Use https:// (certificado SSL)");
      console.log("2. Acesse via localhost ou 127.0.0.1");
      console.log("3. Configure exceções no navegador para IPs locais");
    }

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      console.log("Tentando getUserMedia moderno...");

      // Teste com configuração ideal primeiro
      navigator.mediaDevices
        .getUserMedia({
          video: {
            facingMode: "environment",
            width: { ideal: 640 },
            height: { ideal: 480 },
          },
        })
        .then(function (stream) {
          console.log(
            "✅ Sucesso com configuração ideal! Câmera traseira acessada"
          );
          alert(
            "✅ Sucesso! Câmera traseira funcionando. Tente o scanner novamente."
          );
          stream.getTracks().forEach(function (track) {
            track.stop();
          });
        })
        .catch(function (err) {
          console.log("❌ Erro com configuração ideal:", err);
          console.log("Tentando configuração básica...");

          // Fallback para configuração básica
          return navigator.mediaDevices.getUserMedia({ video: true });
        })
        .then(function (stream) {
          if (stream) {
            console.log(
              "✅ Sucesso com configuração básica! Qualquer câmera acessada"
            );
            alert(
              "✅ Sucesso! Câmera funcionando (básica). Tente o scanner novamente."
            );
            stream.getTracks().forEach(function (track) {
              track.stop();
            });
          }
        })
        .catch(function (err) {
          console.error("❌ Erro final:", err);
          var errorMsg = "❌ Erro ao acessar câmera: " + err.name;
          if (err.message) errorMsg += " - " + err.message;

          if (err.name === "NotAllowedError") {
            errorMsg +=
              "\n\n🔒 Permissão negada. Verifique se você autorizou o acesso à câmera.";
          } else if (
            err.name === "NotSecureError" ||
            err.name === "SecurityError"
          ) {
            errorMsg +=
              "\n\n🔒 Erro de segurança. Em dispositivos móveis na rede local, tente:\n";
            errorMsg += "• Acessar via HTTPS\n";
            errorMsg += "• Configurar exceção no navegador\n";
            errorMsg += "• Usar localhost/127.0.0.1 se possível";
          } else if (err.name === "NotFoundError") {
            errorMsg += "\n\n📷 Nenhuma câmera encontrada no dispositivo.";
          }

          alert(errorMsg);
        });
    } else {
      console.log("API moderna não disponível, tentando legada...");
      var getUserMedia =
        navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia;

      if (getUserMedia) {
        getUserMedia.call(
          navigator,
          { video: true },
          function (stream) {
            console.log("✅ Sucesso com API legada!");
            alert(
              "✅ Sucesso! Câmera funcionando (API legada). Tente o scanner novamente."
            );
            stream.getTracks().forEach(function (track) {
              track.stop();
            });
          },
          function (err) {
            console.error("❌ Erro:", err);
            alert("❌ Erro ao acessar câmera (API legada): " + err);
          }
        );
      } else {
        alert("❌ Nenhuma API de câmera disponível neste navegador");
      }
    }
  };

  function handleError(err) {
    console.error("Erro no scanner:", err);

    var message = "Erro desconhecido.";

    if (
      err.name === "NotAllowedError" ||
      err.name === "PermissionDeniedError"
    ) {
      message =
        "<strong>Permissão negada</strong><br>" +
        "Permita acesso à câmera e recarregue a página.";
    } else if (err.name === "NotFoundError") {
      message =
        "<strong>Câmera não encontrada</strong><br>Verifique se há uma câmera conectada.";
    } else if (err.name === "NotReadableError") {
      message =
        "<strong>Câmera ocupada</strong><br>Feche outros apps que usam a câmera.";
    }

    scannerContainer.innerHTML =
      '<div class="alert alert-danger">' +
      message +
      "<hr><small>Use a digitação manual como alternativa.</small>" +
      "</div>";

    if (codigoInput) {
      codigoInput.focus();
    }
  }

  function stopScanning() {
    isScanning = false;
    scanBtn.textContent = "📷 Escanear Código";

    // Parar stream
    if (stream) {
      var tracks = stream.getTracks();
      for (var i = 0; i < tracks.length; i++) {
        tracks[i].stop();
      }
      stream = null;
    }

    if (videoElement && videoElement.srcObject) {
      var tracks = videoElement.srcObject.getTracks();
      for (var i = 0; i < tracks.length; i++) {
        tracks[i].stop();
      }
      videoElement.srcObject = null;
    }

    if (codeReader && codeReader.reset) {
      try {
        codeReader.reset();
      } catch (err) {
        console.log("Erro ao resetar leitor:", err);
      }
    }

    // Limpar interface
    setTimeout(function () {
      if (scannerContainer && !isScanning) {
        scannerContainer.innerHTML = "";
      }
    }, 1000);
  }

  // Cleanup automático
  function cleanup() {
    stopScanning();
  }

  // Event listeners para cleanup
  if (window.addEventListener) {
    window.addEventListener("beforeunload", cleanup);
    document.addEventListener("visibilitychange", function () {
      if (document.hidden && isScanning) {
        stopScanning();
      }
    });
  } else if (window.attachEvent) {
    window.attachEvent("onbeforeunload", cleanup);
  }

  // Inicializar quando documento estiver pronto
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
