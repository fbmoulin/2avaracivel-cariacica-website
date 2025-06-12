/**
 * Service Worker for 2ª Vara Cível de Cariacica PWA
 * Handles caching, offline functionality, and background sync
 */

const CACHE_NAME = 'vara-civel-v2.4.1';
const STATIC_CACHE = 'static-v2.4.1';
const DYNAMIC_CACHE = 'dynamic-v2.4.1';

// Assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/static/css/style.css',
    '/static/css/modern-consolidated.css',
    '/static/js/main.js',
    '/static/js/modern.js',
    '/static/js/accessibility-enhanced.js',
    '/static/js/chatbot.js',
    '/static/js/pwa-enhanced.js',
    '/static/images/banners/banner_principal.png',
    '/static/images/institutional/forum_cariacica.png',
    '/static/images/chatbot/chatbot_avatar.png',
    '/static/images/icons/consulta_processual.png',
    '/static/images/icons/agendamento.png',
    '/static/images/icons/balcao_virtual.png',
    '/sobre',
    '/faq',
    '/servicos/',
    '/servicos/consulta-processual',
    '/servicos/agendamento'
];

// API endpoints to cache with network-first strategy
const API_ENDPOINTS = [
    '/chatbot/api/message',
    '/admin/status'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Caching static assets...');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('Static assets cached successfully');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('Error caching static assets:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker activating...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Old caches cleaned up');
                return self.clients.claim();
            })
    );
});

// Fetch event - handle requests with different strategies
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Handle different types of requests
    if (request.method === 'GET') {
        if (isStaticAsset(request.url)) {
            // Cache first strategy for static assets
            event.respondWith(cacheFirstStrategy(request));
        } else if (isAPIEndpoint(request.url)) {
            // Network first strategy for API calls
            event.respondWith(networkFirstStrategy(request));
        } else if (isPageRequest(request)) {
            // Stale while revalidate for pages
            event.respondWith(staleWhileRevalidateStrategy(request));
        } else {
            // Default network first
            event.respondWith(networkFirstStrategy(request));
        }
    }
});

// Cache first strategy - for static assets
async function cacheFirstStrategy(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('Cache first strategy failed:', error);
        return await caches.match('/offline.html') || new Response('Offline');
    }
}

// Network first strategy - for API calls and dynamic content
async function networkFirstStrategy(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('Network first strategy failed, trying cache:', error);
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline response for API calls
        if (isAPIEndpoint(request.url)) {
            return new Response(JSON.stringify({
                error: 'Offline',
                message: 'Esta funcionalidade requer conexão com a internet'
            }), {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
            });
        }
        
        return new Response('Offline', { status: 503 });
    }
}

// Stale while revalidate strategy - for pages
async function staleWhileRevalidateStrategy(request) {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cachedResponse = await cache.match(request);
    
    const fetchPromise = fetch(request).then(networkResponse => {
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    }).catch(() => cachedResponse);
    
    return cachedResponse || fetchPromise;
}

// Helper functions
function isStaticAsset(url) {
    return url.includes('/static/') || 
           url.includes('.css') || 
           url.includes('.js') || 
           url.includes('.png') || 
           url.includes('.jpg') || 
           url.includes('.svg');
}

function isAPIEndpoint(url) {
    return API_ENDPOINTS.some(endpoint => url.includes(endpoint));
}

function isPageRequest(request) {
    return request.headers.get('accept').includes('text/html');
}

// Background sync for form submissions
self.addEventListener('sync', event => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'contact-form-sync') {
        event.waitUntil(syncContactForms());
    } else if (event.tag === 'consultation-sync') {
        event.waitUntil(syncConsultations());
    }
});

// Sync contact forms when back online
async function syncContactForms() {
    try {
        const pendingForms = await getStoredData('pending-contact-forms') || [];
        
        for (const formData of pendingForms) {
            try {
                const response = await fetch('/contato', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    console.log('Contact form synced successfully');
                    await removeStoredData('pending-contact-forms', formData.id);
                }
            } catch (error) {
                console.log('Failed to sync contact form:', error);
            }
        }
    } catch (error) {
        console.log('Background sync failed:', error);
    }
}

// Sync process consultations when back online
async function syncConsultations() {
    try {
        const pendingConsultations = await getStoredData('pending-consultations') || [];
        
        for (const consultation of pendingConsultations) {
            try {
                const response = await fetch('/servicos/consulta-processual', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(consultation)
                });
                
                if (response.ok) {
                    console.log('Consultation synced successfully');
                    await removeStoredData('pending-consultations', consultation.id);
                }
            } catch (error) {
                console.log('Failed to sync consultation:', error);
            }
        }
    } catch (error) {
        console.log('Background sync failed:', error);
    }
}

// IndexedDB helpers for offline storage
async function getStoredData(storeName) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('VaraCivelDB', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const getRequest = store.getAll();
            
            getRequest.onsuccess = () => resolve(getRequest.result);
            getRequest.onerror = () => reject(getRequest.error);
        };
        
        request.onupgradeneeded = () => {
            const db = request.result;
            if (!db.objectStoreNames.contains(storeName)) {
                db.createObjectStore(storeName, { keyPath: 'id' });
            }
        };
    });
}

async function removeStoredData(storeName, id) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('VaraCivelDB', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const deleteRequest = store.delete(id);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
    });
}

// Push notification handling
self.addEventListener('push', event => {
    console.log('Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'Nova atualização disponível',
        icon: '/static/images/icons/icon-192x192.png',
        badge: '/static/images/icons/icon-72x72.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Ver detalhes',
                icon: '/static/images/icons/icon-72x72.png'
            },
            {
                action: 'close',
                title: 'Fechar',
                icon: '/static/images/icons/icon-72x72.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('2ª Vara Cível de Cariacica', options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
    console.log('Notification clicked:', event);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Message handling for communication with main thread
self.addEventListener('message', event => {
    console.log('Service Worker received message:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(DYNAMIC_CACHE)
                .then(cache => cache.addAll(event.data.payload))
        );
    }
});

console.log('Service Worker loaded successfully');