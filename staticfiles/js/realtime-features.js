/**
 * Real-time Features for We Cafe
 * Includes: Live notifications, cart updates, order tracking, and more
 */

// Real-time Notification System
class NotificationManager {
    constructor() {
        this.notificationContainer = null;
        this.init();
    }

    init() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(container);
            this.notificationContainer = container;
        }
    }

    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification-item`;
        notification.style.cssText = `
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideInRight 0.3s ease-out;
        `;
        
        const icons = {
            success: 'fa-check-circle',
            danger: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        notification.innerHTML = `
            <i class="fas ${icons[type]} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        this.notificationContainer.appendChild(notification);
        
        // Auto remove after duration
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }
}

// Live Cart Counter
class CartManager {
    constructor() {
        this.cartBadge = document.querySelector('.cart-badge');
        this.init();
    }

    init() {
        // Update cart count on page load
        this.updateCartCount();
        
        // Listen for cart updates
        document.addEventListener('cartUpdated', () => {
            this.updateCartCount();
        });
    }

    async updateCartCount() {
        try {
            const response = await fetch('/cart/count/');
            const data = await response.json();
            
            if (this.cartBadge) {
                this.cartBadge.textContent = data.count;
                
                // Animate badge
                this.cartBadge.style.transform = 'scale(1.3)';
                setTimeout(() => {
                    this.cartBadge.style.transform = 'scale(1)';
                }, 200);
            }
        } catch (error) {
            console.error('Error updating cart count:', error);
        }
    }

    addToCart(itemId, quantity = 1) {
        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            body: JSON.stringify({ item_id: itemId, quantity: quantity })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                notificationManager.show('Item added to cart!', 'success');
                document.dispatchEvent(new Event('cartUpdated'));
            }
        })
        .catch(error => {
            notificationManager.show('Error adding item to cart', 'danger');
        });
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

// Live Search with Debounce
class LiveSearch {
    constructor(inputSelector, resultsSelector) {
        this.input = document.querySelector(inputSelector);
        this.results = document.querySelector(resultsSelector);
        this.debounceTimer = null;
        
        if (this.input) {
            this.init();
        }
    }

    init() {
        this.input.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.search(e.target.value);
            }, 300);
        });
    }

    async search(query) {
        if (query.length < 2) {
            this.results.innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/menu/search/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            this.displayResults(data.results);
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    displayResults(results) {
        if (results.length === 0) {
            this.results.innerHTML = '<div class="p-3 text-muted">No items found</div>';
            return;
        }

        this.results.innerHTML = results.map(item => `
            <a href="/menu/${item.slug}/" class="list-group-item list-group-item-action">
                <div class="d-flex align-items-center">
                    <img src="${item.image}" alt="${item.name}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" class="me-3">
                    <div>
                        <h6 class="mb-0">${item.name}</h6>
                        <small class="text-muted">${item.category}</small>
                        <div class="text-primary fw-bold">₹${item.price}</div>
                    </div>
                </div>
            </a>
        `).join('');
    }
}

// Order Status Tracker
class OrderTracker {
    constructor() {
        this.orderStatusElements = document.querySelectorAll('[data-order-id]');
        this.init();
    }

    init() {
        if (this.orderStatusElements.length > 0) {
            this.startTracking();
        }
    }

    startTracking() {
        // Check order status every 30 seconds
        setInterval(() => {
            this.updateOrderStatuses();
        }, 30000);
    }

    async updateOrderStatuses() {
        for (const element of this.orderStatusElements) {
            const orderId = element.dataset.orderId;
            
            try {
                const response = await fetch(`/orders/${orderId}/status/`);
                const data = await response.json();
                
                if (data.status !== element.dataset.currentStatus) {
                    this.updateOrderUI(element, data);
                    notificationManager.show(`Order #${orderId} status updated: ${data.status_display}`, 'info');
                }
            } catch (error) {
                console.error('Error tracking order:', error);
            }
        }
    }

    updateOrderUI(element, data) {
        element.dataset.currentStatus = data.status;
        
        // Update status badge
        const badge = element.querySelector('.status-badge');
        if (badge) {
            badge.className = `badge status-badge status-${data.status}`;
            badge.textContent = data.status_display;
        }
        
        // Update progress bar if exists
        const progressBar = element.querySelector('.order-progress');
        if (progressBar) {
            progressBar.style.width = `${data.progress}%`;
        }
    }
}

// Wishlist Manager
class WishlistManager {
    constructor() {
        this.wishlistButtons = document.querySelectorAll('.wishlist-btn');
        this.init();
    }

    init() {
        this.wishlistButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const itemId = btn.dataset.itemId;
                this.toggleWishlist(itemId, btn);
            });
        });
    }

    async toggleWishlist(itemId, button) {
        try {
            const response = await fetch('/wishlist/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ item_id: itemId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Toggle heart icon
                const icon = button.querySelector('i');
                if (data.added) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    button.classList.add('active');
                    notificationManager.show('Added to wishlist!', 'success');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    button.classList.remove('active');
                    notificationManager.show('Removed from wishlist', 'info');
                }
            }
        } catch (error) {
            notificationManager.show('Error updating wishlist', 'danger');
        }
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

// Quick View Modal
class QuickView {
    constructor() {
        this.quickViewButtons = document.querySelectorAll('.quick-view-btn');
        this.init();
    }

    init() {
        this.quickViewButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const itemId = btn.dataset.itemId;
                this.showQuickView(itemId);
            });
        });
    }

    async showQuickView(itemId) {
        try {
            const response = await fetch(`/menu/item/${itemId}/quick-view/`);
            const html = await response.text();
            
            // Create modal
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = html;
            document.body.appendChild(modal);
            
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            // Remove modal from DOM after hiding
            modal.addEventListener('hidden.bs.modal', () => {
                modal.remove();
            });
        } catch (error) {
            notificationManager.show('Error loading item details', 'danger');
        }
    }
}

// Auto-save Cart (for logged-in users)
class AutoSaveCart {
    constructor() {
        this.saveTimer = null;
        this.init();
    }

    init() {
        // Listen for cart changes
        document.addEventListener('cartChanged', () => {
            this.scheduleAutoSave();
        });
    }

    scheduleAutoSave() {
        clearTimeout(this.saveTimer);
        this.saveTimer = setTimeout(() => {
            this.saveCart();
        }, 2000); // Save after 2 seconds of inactivity
    }

    async saveCart() {
        const cartItems = this.getCartItems();
        
        try {
            await fetch('/cart/auto-save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ items: cartItems })
            });
        } catch (error) {
            console.error('Auto-save error:', error);
        }
    }

    getCartItems() {
        // Get cart items from the page
        const items = [];
        document.querySelectorAll('.cart-item').forEach(item => {
            items.push({
                id: item.dataset.itemId,
                quantity: item.querySelector('.quantity-input').value
            });
        });
        return items;
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

// Initialize all features when DOM is ready
let notificationManager, cartManager, orderTracker, wishlistManager, quickView, autoSaveCart;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all managers
    notificationManager = new NotificationManager();
    cartManager = new CartManager();
    orderTracker = new OrderTracker();
    wishlistManager = new WishlistManager();
    quickView = new QuickView();
    autoSaveCart = new AutoSaveCart();
    
    // Initialize live search if search input exists
    if (document.querySelector('#live-search-input')) {
        new LiveSearch('#live-search-input', '#live-search-results');
    }
    
    console.log('Real-time features initialized');
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification-item {
        transition: all 0.3s ease;
    }
    
    .cart-badge {
        transition: transform 0.2s ease;
    }
    
    .wishlist-btn.active i {
        color: #dc3545;
        animation: heartBeat 0.3s ease;
    }
    
    @keyframes heartBeat {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.3); }
    }
`;
document.head.appendChild(style);
