// The handbook has moved to https://rlh-tag.github.io/
// This worker replaces the old offline copy: it clears the stored files,
// sends any open copy to the new address, and removes itself.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) await caches.delete(key);
    await self.clients.claim();
    for (const client of await self.clients.matchAll({type: "window"})) {
      const hash = new URL(client.url).hash;
      try { await client.navigate("https://rlh-tag.github.io/" + hash); } catch (e) {}
    }
    await self.registration.unregister();
  })());
});
