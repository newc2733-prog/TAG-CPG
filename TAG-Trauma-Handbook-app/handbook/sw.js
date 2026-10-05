// This address has moved to the top of the site. Remove the old offline copy and send open pages there.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith("tag-handbook-")) await caches.delete(k);
    await self.registration.unregister();
    for (const c of await self.clients.matchAll({type: "window"})) c.navigate("../../");
  })());
});
