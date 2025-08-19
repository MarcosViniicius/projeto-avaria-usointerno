const CACHE_NAME = "sistema-avarias-v1";
const urlsToCache = [
  "/",
  "/registrar/hortifruti",
  "/registrar/interno",
  "/static/js/scanner.js",
  "/static/manifest.json",
  "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
  "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
  "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js",
];

// Instalar Service Worker
self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      console.log("Cache aberto");
      return cache.addAll(urlsToCache);
    })
  );
});

// Buscar recursos
self.addEventListener("fetch", function (event) {
  event.respondWith(
    caches.match(event.request).then(function (response) {
      // Cache hit - retorna resposta
      if (response) {
        return response;
      }

      return fetch(event.request).then(function (response) {
        // Verifica se recebemos uma resposta válida
        if (!response || response.status !== 200 || response.type !== "basic") {
          return response;
        }

        // IMPORTANTE: Clone a resposta. Uma resposta é um stream
        // e como queremos tanto o browser quanto o cache para consumir a resposta
        // precisamos cloná-la para ter duas streams.
        var responseToCache = response.clone();

        caches.open(CACHE_NAME).then(function (cache) {
          cache.put(event.request, responseToCache);
        });

        return response;
      });
    })
  );
});

// Atualizar Service Worker
self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (cacheNames) {
      return Promise.all(
        cacheNames.map(function (cacheName) {
          if (cacheName !== CACHE_NAME) {
            console.log("Removendo cache antigo:", cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
