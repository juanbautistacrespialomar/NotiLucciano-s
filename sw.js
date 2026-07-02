/* NotiLucciano's — service worker
   Estrategia:
   - HTML y datos (ediciones.json + ediciones/*.json): NETWORK-FIRST.
     Trae lo último si hay señal; si no, sirve lo último visto (offline).
   - Íconos y fuentes: CACHE-FIRST (casi nunca cambian).
   Para forzar que todos actualicen el "cascarón", subí CACHE una versión
   (v1 -> v2). Eso limpia el cache viejo en el próximo arranque. */
const CACHE = 'notilucc-v4';
const SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/apple-touch-icon.png',
  './icons/favicon.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)));
});

// El cliente avisa "actualizá ahora" (cuando el usuario toca el cartel).
self.addEventListener('message', e => {
  if (e.data && e.data.type === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function esDato(url){
  return url.pathname.endsWith('/ediciones.json') || /\/ediciones\/[^/]+\.json$/.test(url.pathname);
}
function esNavegacion(req){
  return req.mode === 'navigate' || req.destination === 'document';
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Fuentes de Google: cache-first con refresco en segundo plano.
  if (url.hostname.includes('fonts.googleapis.com') || url.hostname.includes('fonts.gstatic.com')) {
    e.respondWith(
      caches.open(CACHE).then(c => c.match(req).then(hit => {
        const net = fetch(req).then(res => { c.put(req, res.clone()); return res; }).catch(() => hit);
        return hit || net;
      }))
    );
    return;
  }

  // Otros orígenes (ej: reproductor de Spotify): directo a la red, sin cachear.
  if (url.origin !== self.location.origin) return;

  // HTML y datos: network-first, con fallback al cache (offline).
  if (esNavegacion(req) || esDato(url)) {
    e.respondWith(
      fetch(req).then(res => {
        const copia = res.clone();
        caches.open(CACHE).then(c => c.put(req, copia));
        return res;
      }).catch(() => caches.match(req).then(hit => hit || caches.match('./index.html')))
    );
    return;
  }

  // Estáticos propios (íconos, fotos): cache-first.
  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(res => {
      const copia = res.clone();
      caches.open(CACHE).then(c => c.put(req, copia));
      return res;
    }))
  );
});
