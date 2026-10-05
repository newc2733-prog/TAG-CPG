// Offline support. A new build changes VERSION, which makes phones fetch the new files.
const VERSION = "20261005-1643";
const CACHE = "tag-handbook-" + VERSION;
const FILES = [
  "./",
  "index.html",
  "manifest.webmanifest",
  "fig/code-red-tca.jpg",
  "fig/da-aintree.jpg",
  "fig/da-airtraq.jpg",
  "fig/da-ambu.jpg",
  "fig/da-cmac.jpg",
  "fig/da-das.jpg",
  "fig/da-epistat.jpg",
  "fig/da-mcgrath.jpg",
  "fig/drown-patho.jpg",
  "fig/neck-zones.jpg",
  "fig/olv-dlt.jpg",
  "fig/olv-insertion.jpg",
  "fig/olv-photos.jpg",
  "fig/olv-trouble.jpg",
  "fig/rib-catheter.jpg",
  "fig/rotem-algorithm.jpg",
  "fig/rsi-checklist.jpg",
  "fig/rsi-das.jpg",
  "fig/rsi-fona.jpg",
  "fig/sci-asia.jpg",
  "fig/sci-infographic.jpg",
  "fig/vasc-mac.jpg",
  "fig/vasc-ric.jpg",
  "fig/vasc-scv.jpg",
  "fonts/lexend-latin-ext-wght-normal.woff2",
  "fonts/lexend-latin-wght-normal.woff2",
  "icons/apple-touch-icon.png",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/icon-maskable-512.png"
];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES.map(f => new Request(f, {cache: "reload"})))).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith("tag-handbook-") && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  const req = e.request.mode === "navigate" ? "index.html" : e.request;
  e.respondWith(caches.open(CACHE).then(c => c.match(req, {ignoreSearch: true})).then(hit => hit || fetch(e.request)));
});
