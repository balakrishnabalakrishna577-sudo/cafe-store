/**
 * Advanced Real-time Features for We Cafe
 * Includes: Live chat, push notifications, real-time delivery tracking, and more
 */

// Live Delivery Tracking with Map
class DeliveryTracker {
    constructor() {
        this.trackingInterval = null;
        this.mapElement = document.getElementById('delivery-map');
        this.init();
    }

    init() {
        if (this.mapElement) {
            this.startTracking();
        }
    }

    startTracking() {
        // Update delivery location every 10 seconds
        this.trackingInterval = setInterval(() => {
            this.updateDeliveryLocation();
        }, 10000);
    }

    async updateDeliveryLocation() {
        const orderId = this.mapElement.dataset.orderId;
        
        try {
            const response = await fetch(`/orders/${orderId}/delivery-location/`);
            const data = await response.json();
            
            if (data.location) {
                this.updateMap(data.location);
                this.updateETA(data.eta);
            }
        } catch (error) {
            console.error('Error tracking delivery:', error);
        }
    }

    updateMap(location) {
        // Update map marker position
        // This would integrate with Google Maps or similar
        console.log('Delivery location updated:', location);
    }

    updateETA(eta) {
        const etaElement = document.getElementById('delivery-eta');
        if (etaElement) {
            etaElement.textContent = eta;
        }
    }

    stopTracking() {
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
        }
    }
}

// Real-time Notifications with Web Push
class PushNotificationManager {
    constructor() {
        this.permission = Notification.permission;
        this.init();
    }

    init() {
        // Check if browser supports notifications
        if (!('Notification' in window)) {
            console.log('This browser does not support notifications');
            return;
        }

        // Request permission if not granted
        if (this.permission === 'default') {
            this.requestPermission();
        }
    }

    async requestPermission() {
        const permission = await Notification.requestPermission();
        this.permission = permission;
        
        if (permission === 'granted') {
            notificationManager.show('Notifications enabled!', 'success');
        }
    }

    showNotification(title, options = {}) {
        if (this.permission === 'granted') {
            const notification = new Notification(title, {
                icon: '/static/images/logo.png',
                badge: '/static/images/badge.png',
                ...options
            });

            notification.onclick = function(event) {
                event.preventDefault();
                window.focus();
                if (options.url) {
                    window.location.href = options.url;
                }
            };
        }
    }
}

// Live Chat Support
class LiveChatSupport {
    constructor() {
        this.chatWidget = null;
        this.messages = [];
        this.isOpen = false;
        this.init();
    }

    init() {
        this.createChatWidget();
        this.attachEventListeners();
    }

    createChatWidget() {
        const widget = document.createElement('div');
        widget.id = 'live-chat-widget';
        widget.innerHTML = `
            <div class="chat-toggle" id="chat-toggle">
                <i class="fas fa-comments"></i>
                <span class="chat-badge" id="chat-badge" style="display: none;">0</span>
            </div>
            <div class="chat-window" id="chat-window" style="display: none;">
                <div class="chat-header">
                    <h6><i class="fas fa-headset me-2"></i>Live Support</h6>
                    <button class="btn-close btn-close-white" id="chat-close"></button>
                </div>
                <div class="chat-messages" id="chat-messages">
                    <div class="chat-message bot">
                        <div class="message-content">
                            <p>Hi! How can we help you today?</p>
                            <small class="text-muted">Just now</small>
                        </div>
                    </div>
                </div>
                <div class="chat-input">
                    <input type="text" id="chat-input-field" placeholder="Type your message..." class="form-control">
                    <button id="chat-send" class="btn btn-primary">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        `;

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            #live-chat-widget {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 9998;
            }
            
            .chat-toggle {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                transition: transform 0.3s;
                position: relative;
            }
            
            .chat-toggle:hover {
                transform: scale(1.1);
            }
            
            .chat-badge {
                position: absolute;
                top: -5px;
                right: -5px;
                background: #dc3545;
                color: white;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
            }
            
            .chat-window {
                position: absolute;
                bottom: 80px;
                right: 0;
                width: 350px;
                height: 500px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.2);
                display: flex;
                flex-direction: column;
                animation: slideUp 0.3s ease-out;
            }
            
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                border-radius: 12px 12px 0 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .chat-header h6 {
                margin: 0;
            }
            
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
                background: #f8f9fa;
            }
            
            .chat-message {
                margin-bottom: 15px;
                display: flex;
            }
            
            .chat-message.bot {
                justify-content: flex-start;
            }
            
            .chat-message.user {
                justify-content: flex-end;
            }
            
            .message-content {
                max-width: 70%;
                padding: 10px 15px;
                border-radius: 12px;
                background: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .chat-message.user .message-content {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .message-content p {
                margin: 0;
                font-size: 14px;
            }
            
            .message-content small {
                font-size: 11px;
            }
            
            .chat-input {
                display: flex;
                padding: 15px;
                border-top: 1px solid #e0e0e0;
                background: white;
                border-radius: 0 0 12px 12px;
            }
            
            .chat-input input {
                flex: 1;
                border: 1px solid #e0e0e0;
                border-radius: 20px;
                padding: 8px 15px;
                margin-right: 10px;
            }
            
            .chat-input button {
                border-radius: 50%;
                width: 40px;
                height: 40px;
                padding: 0;
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(widget);
        
        this.chatWidget = widget;
    }

    attachEventListeners() {
        const toggle = document.getElementById('chat-toggle');
        const close = document.getElementById('chat-close');
        const send = document.getElementById('chat-send');
        const input = document.getElementById('chat-input-field');

        toggle.addEventListener('click', () => this.toggleChat());
        close.addEventListener('click', () => this.toggleChat());
        send.addEventListener('click', () => this.sendMessage());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    toggleChat() {
        const window = document.getElementById('chat-window');
        this.isOpen = !this.isOpen;
        window.style.display = this.isOpen ? 'flex' : 'none';
        
        if (this.isOpen) {
            document.getElementById('chat-input-field').focus();
        }
    }

    sendMessage() {
        const input = document.getElementById('chat-input-field');
        const message = input.value.trim();
        
        if (message) {
            this.addMessage(message, 'user');
            input.value = '';
            
            // Simulate bot response
            setTimeout(() => {
                this.addMessage('Thank you for your message. Our team will respond shortly.', 'bot');
            }, 1000);
        }
    }

    addMessage(text, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${text}</p>
                <small class="text-muted">Just now</small>
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Smart Recommendations Engine
class RecommendationEngine {
    constructor() {
        this.userPreferences = this.loadPreferences();
        this.init();
    }

    init() {
        this.trackUserBehavior();
        this.showRecommendations();
    }

    trackUserBehavior() {
        // Track viewed items
        document.querySelectorAll('.menu-item-card').forEach(card => {
            card.addEventListener('click', () => {
                const itemId = card.dataset.itemId;
                const category = card.dataset.category;
                this.recordView(itemId, category);
            });
        });
    }

    recordView(itemId, category) {
        if (!this.userPreferences.viewedItems) {
            this.userPreferences.viewedItems = [];
        }
        
        this.userPreferences.viewedItems.push({
            itemId,
            category,
            timestamp: Date.now()
        });
        
        // Keep only last 50 views
        if (this.userPreferences.viewedItems.length > 50) {
            this.userPreferences.viewedItems.shift();
        }
        
        this.savePreferences();
    }

    async showRecommendations() {
        const container = document.getElementById('recommendations-container');
        if (!container) return;

        try {
            const response = await fetch('/menu/recommendations/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify(this.userPreferences)
            });
            
            const data = await response.json();
            this.displayRecommendations(data.recommendations);
        } catch (error) {
            console.error('Error loading recommendations:', error);
        }
    }

    displayRecommendations(items) {
        const container = document.getElementById('recommendations-container');
        if (!container || items.length === 0) return;

        container.innerHTML = `
            <h4 class="mb-3"><i class="fas fa-magic me-2"></i>Recommended for You</h4>
            <div class="row">
                ${items.map(item => `
                    <div class="col-md-3 mb-3">
                        <div class="card menu-item-card" data-item-id="${item.id}">
                            <img src="${item.image}" class="card-img-top" alt="${item.name}">
                            <div class="card-body">
                                <h6>${item.name}</h6>
                                <p class="text-primary fw-bold">₹${item.price}</p>
                                <button class="btn btn-sm btn-primary w-100" onclick="cartManager.addToCart(${item.id})">
                                    Add to Cart
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    loadPreferences() {
        const saved = localStorage.getItem('userPreferences');
        return saved ? JSON.parse(saved) : {};
    }

    savePreferences() {
        localStorage.setItem('userPreferences', JSON.stringify(this.userPreferences));
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Voice Search Feature
class VoiceSearch {
    constructor() {
        this.recognition = null;
        this.init();
    }

    init() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            
            this.setupVoiceButton();
        }
    }

    setupVoiceButton() {
        const searchInput = document.querySelector('#live-search-input');
        if (!searchInput) return;

        const voiceBtn = document.createElement('button');
        voiceBtn.className = 'btn btn-outline-primary voice-search-btn';
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceBtn.style.cssText = 'position: absolute; right: 10px; top: 50%; transform: translateY(-50%);';
        
        searchInput.parentElement.style.position = 'relative';
        searchInput.parentElement.appendChild(voiceBtn);

        voiceBtn.addEventListener('click', () => this.startListening());
    }

    startListening() {
        if (!this.recognition) return;

        this.recognition.start();
        notificationManager.show('Listening...', 'info', 2000);

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.querySelector('#live-search-input').value = transcript;
            document.querySelector('#live-search-input').dispatchEvent(new Event('input'));
        };

        this.recognition.onerror = (event) => {
            notificationManager.show('Voice search error', 'danger');
        };
    }
}

// Offline Mode Support
class OfflineManager {
    constructor() {
        this.isOnline = navigator.onLine;
        this.init();
    }

    init() {
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
        
        if (!this.isOnline) {
            this.showOfflineMessage();
        }
    }

    handleOnline() {
        this.isOnline = true;
        
        // Remove offline banner
    }

    handleOffline() {
        this.isOnline = false;
        this.showOfflineMessage();
    }

    showOfflineMessage() {
        const banner = document.createElement('div');
        banner.id = 'offline-banner';
        banner.className = 'alert alert-warning';
        banner.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; z-index: 10000; margin: 0; border-radius: 0;';
        banner.innerHTML = `
            <div class="container">
                <i class="fas fa-wifi-slash me-2"></i>
                You are currently offline. Some features may be limited.
            </div>
        `;
        document.body.prepend(banner);
    }

    async syncOfflineData() {
        // Sync any offline cart changes
        const offlineCart = localStorage.getItem('offlineCart');
        if (offlineCart) {
            try {
                await fetch('/cart/sync/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    },
                    body: offlineCart
                });
                localStorage.removeItem('offlineCart');
            } catch (error) {
                console.error('Sync error:', error);
            }
        }

        // Remove offline banner
        const banner = document.getElementById('offline-banner');
        if (banner) banner.remove();
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize all advanced features
let deliveryTracker, pushNotifications, liveChat, recommendations, voiceSearch, offlineManager;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize advanced features
    deliveryTracker = new DeliveryTracker();
    pushNotifications = new PushNotificationManager();
    liveChat = new LiveChatSupport();
    recommendations = new RecommendationEngine();
    voiceSearch = new VoiceSearch();
    offlineManager = new OfflineManager();
    
    console.log('Advanced features initialized');
});
