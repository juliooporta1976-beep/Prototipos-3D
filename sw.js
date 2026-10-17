// MercaNica · offline con la última versión vista
const C = 'mercanica-v3';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(
  caches.keys()
    .then(k => Promise.all(k.filter(x => x !== C).map(x => caches.delete(x))))
    .then(() => self.clients.claim())
));

self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET') return;
  const url = new URL(r.url);
  if (url.origin !== location.origin) return;

  const isData = url.pathname.endsWith('.json');
  const isNav  = r.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname.endsWith('/');

  if (isData || isNav) {
    e.respondWith(
      fetch(r).then(res => {
        if (res.ok) {
          const cp = res.clone();
          caches.open(C).then(c => c.put(r, cp));
        }
        return res;
      }).catch(() => caches.match(r).then(m => m || (isNav ? caches.match('MercaNica.html') : undefined)))
    );
    return;
  }

  e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => {
    if (res.ok) {
      const cp = res.clone();
      caches.open(C).then(c => c.put(r, cp));
    }
    return res;
  })));
});
