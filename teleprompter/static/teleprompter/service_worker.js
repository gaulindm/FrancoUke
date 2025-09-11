const CACHE_NAME = 'teleprompter-v1';
const ASSETS_TO_CACHE = [
  '/static/teleprompter/css/teleprompter.css',
  '/static/teleprompter/js/teleprompter.js',
  '/static/teleprompter/manifest.json'
  // add icons & other static files you want offline
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS_TO_CACHE))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  // fast cache-first strategy for static assets
  event.respondWith(
    caches.match(event.request).then(resp => resp || fetch(event.request))
  );
});
