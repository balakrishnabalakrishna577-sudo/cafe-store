// Basic service worker for Spices of India Cuisine

self.addEventListener('install', event => {
  // Activate immediately after installation
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  // Take control of uncontrolled clients
  event.waitUntil(self.clients.claim());
});

// Simple passthrough fetch handler (no aggressive caching to avoid issues)
self.addEventListener('fetch', event => {
  event.respondWith(fetch(event.request));
});

