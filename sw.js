/* Майстерня: кеш оболонки, щоб застосунок відкривався без інтернету. Дані (Firestore) кешує сам Firebase. */
var V = "m1";
self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.filter(function (k) { return k !== V; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener("fetch", function (e) {
  var r = e.request;
  if (r.method !== "GET") return;
  var u = new URL(r.url);
  var same = u.origin === location.origin;
  var cdn = u.hostname === "www.gstatic.com" || u.hostname === "fonts.googleapis.com" || u.hostname === "fonts.gstatic.com";
  if (!same && !cdn) return;
  if (same) {
    if (u.pathname.slice(-4) === ".enc") return;
    e.respondWith(fetch(r.url, { cache: "no-cache" }).then(function (res) {
      if (res.ok) { var c = res.clone(); caches.open(V).then(function (ca) { ca.put(r, c); }); }
      return res;
    }).catch(function () { return caches.match(r, { ignoreSearch: true }).then(function (m) { return m || caches.match("./"); }); }));
  } else {
    e.respondWith(caches.match(r).then(function (m) {
      return m || fetch(r).then(function (res) {
        if (res.ok || res.type === "opaque") { var c = res.clone(); caches.open(V).then(function (ca) { ca.put(r, c); }); }
        return res;
      });
    }));
  }
});
