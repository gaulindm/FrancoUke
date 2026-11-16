// StrumSphere service worker: lets the songbook work without wifi.
// Bump CACHE (v2, v3...) after deploying changed JS/CSS so the iPad picks it up.
const CACHE = "strumsphere-v1";
const CDN_HOSTS = [
  "cdn.jsdelivr.net", "unpkg.com", "cdnjs.cloudflare.com",
  "maxcdn.bootstrapcdn.com",
  "fonts.googleapis.com", "fonts.gstatic.com",
];

self.addEventListener("install", () => self.skipWaiting());

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Save a copy of a response. Redirected responses are skipped because
// Safari refuses to show a redirected response served from the cache.
function store(req, r) {
  if (r.redirected) return r;
  if (r.ok || r.type === "opaque") {
    const copy = r.clone();
    caches.open(CACHE).then(c => c.put(req, copy));
  }
  return r;
}

// Django sends "Vary: Cookie", which can stop a saved page from matching, so ignore it.
function fromCache(req, ignoreSearch) {
  return caches.match(req, { ignoreVary: true, ignoreSearch: !!ignoreSearch });
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  if (req.headers.get("HX-Request")) return;   // leave htmx requests alone

  const url = new URL(req.url);

  // CDN files and your own static files: saved copy first
  if (CDN_HOSTS.includes(url.hostname) ||
      (url.origin === location.origin && url.pathname.startsWith("/static/"))) {
    e.respondWith(
      fromCache(req).then(hit => hit || fetch(req).then(r => store(req, r)))
    );
    return;
  }

  if (url.origin !== location.origin) return;

  // Pages: network first, fall back to the saved copy when offline
  e.respondWith(
    fetch(req)
      .then(r => store(req, r))
      .catch(() => fromCache(req).then(hit => hit || fromCache(req, true)))
  );
});