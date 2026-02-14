// Main JavaScript for Cafe Delivery

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeNavbarEffects();
    initializeSearch();
    initializeNotifications();
    initializeScrollEffects();
    initializeFormValidation();
    initializeLazyLoading();
    initializeMobileOptimizations();
    initializeMobileSidebar();
    
    // Add CSRF token to all AJAX requests
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        window.csrfToken = csrfToken.value;
    }
});

// Modern Navbar Effects
function initializeNavbarEffects() {
    const navbar = document.querySelector('.main-navbar');
    if (!navbar) return;
    
    // Navbar scroll effect with smooth behavior
    let lastScrollTop = 0;
    let ticking = false;
    
    function updateNavbar() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Add scrolled class for styling
        if (scrollTop > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        // Smooth hide/show on scroll
        if (scrollTop > lastScrollTop && scrollTop > 200 && Math.abs(scrollTop - lastScrollTop) > 5) {
            // Scrolling down fast - hide navbar
            navbar.style.transform = 'translateY(-100%)';
            navbar.style.transition = 'transform 0.3s ease-in-out';
        } else if (scrollTop < lastScrollTop || scrollTop <= 100) {
            // Scrolling up or near top - show navbar
            navbar.style.transform = 'translateY(0)';
            navbar.style.transition = 'transform 0.3s ease-in-out';
        }
        
        lastScrollTop = scrollTop;
        ticking = false;
    }
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateNavbar);
            ticking = true;
        }
    });
    
    // Ensure navbar is always visible when hovering
    navbar.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(0)';
    });
    
    // Brand logo smooth animation
    const brandLogo = document.querySelector('.brand-logo');
    if (brandLogo) {
        brandLogo.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.brand-icon');
            if (icon) {
                icon.style.transition = 'transform 0.3s ease';
                icon.style.transform = 'rotate(360deg) scale(1.1)';
            }
        });
        
        brandLogo.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.brand-icon');
            if (icon) {
                icon.style.transition = 'transform 0.3s ease';
                icon.style.transform = 'rotate(0deg) scale(1)';
            }
        });
    }
    
    // Navigation links smooth hover effects
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transition = 'transform 0.2s ease';
            this.style.transform = 'translateY(-2px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transition = 'transform 0.2s ease';
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Initialize Bootstrap dropdowns - let Bootstrap handle it
    // Bootstrap 5 handles dropdowns automatically with data-bs-toggle="dropdown"
    console.log('Bootstrap dropdowns initialized');
    
    // Cart badge smooth animation
    const cartBadge = document.querySelector('.notification-count');
    if (cartBadge) {
        // Animate when cart count changes
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' || mutation.type === 'characterData') {
                    cartBadge.style.animation = 'none';
                    setTimeout(() => {
                        cartBadge.style.animation = 'pulse 0.6s ease-in-out';
                    }, 10);
                }
            });
        });
        
        observer.observe(cartBadge, {
            childList: true,
            characterData: true,
            subtree: true
        });
    }
}

// Search functionality
function initializeSearch() {
    // Desktop search
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    // Mobile search
    const searchInputMobile = document.getElementById('search-input-mobile');
    const searchResultsMobile = document.getElementById('search-results-mobile');
    
    let searchTimeout;
    
    // Initialize desktop search
    if (searchInput && searchResults) {
        initializeSearchInput(searchInput, searchResults, 'desktop');
    }
    
    // Initialize mobile search
    if (searchInputMobile && searchResultsMobile) {
        initializeSearchInput(searchInputMobile, searchResultsMobile, 'mobile');
    }
    
    // Sync search inputs (clear other when typing in one)
    function syncSearchInputs(activeInput, inactiveInput) {
        if (activeInput && inactiveInput) {
            activeInput.addEventListener('input', function() {
                if (this.value.length > 0) {
                    inactiveInput.value = '';
                    const inactiveResults = document.querySelector(`#${inactiveInput.id.replace('input', 'results')}`);
                    if (inactiveResults) {
                        inactiveResults.style.display = 'none';
                    }
                }
            });
        }
    }
    
    // Set up syncing between desktop and mobile search
    syncSearchInputs(searchInput, searchInputMobile);
    syncSearchInputs(searchInputMobile, searchInput);
    
    function initializeSearchInput(input, results, type) {
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                results.style.display = 'none';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                performSearch(query, results);
            }, 300);
        });
        
        // Hide search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!input.contains(e.target) && !results.contains(e.target)) {
                results.style.display = 'none';
            }
        });
        
        // Handle keyboard navigation
        input.addEventListener('keydown', function(e) {
            const resultItems = results.querySelectorAll('.search-result-item');
            let currentIndex = -1;
            
            // Find currently selected item
            resultItems.forEach((item, index) => {
                if (item.classList.contains('selected')) {
                    currentIndex = index;
                }
            });
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                currentIndex = Math.min(currentIndex + 1, resultItems.length - 1);
                updateSelection(resultItems, currentIndex);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                currentIndex = Math.max(currentIndex - 1, -1);
                updateSelection(resultItems, currentIndex);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (currentIndex >= 0 && resultItems[currentIndex]) {
                    resultItems[currentIndex].click();
                }
            } else if (e.key === 'Escape') {
                results.style.display = 'none';
                input.blur();
            }
        });
        
        // Handle touch events for mobile
        if ('ontouchstart' in window) {
            input.addEventListener('touchstart', function() {
                this.focus();
            });
            
            results.addEventListener('touchstart', function(e) {
                e.preventDefault(); // Prevent default touch behavior
            });
            
            // Close mobile menu when search is focused (if in mobile menu)
            if (type === 'mobile') {
                input.addEventListener('focus', function() {
                    // Don't close the navbar collapse, just ensure search is visible
                    this.scrollIntoView({ behavior: 'smooth', block: 'center' });
                });
            }
        }
        
        // Handle mobile-specific behaviors
        if (type === 'mobile') {
            // Ensure mobile search results are properly positioned
            input.addEventListener('focus', function() {
                setTimeout(() => {
                    if (results.style.display === 'block') {
                        results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                }, 100);
            });
        }
        
        // Auto-hide results when scrolling (mobile)
        if (type === 'mobile' && window.innerWidth < 768) {
            let scrollTimeout;
            window.addEventListener('scroll', function() {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    if (results.style.display === 'block') {
                        results.style.display = 'none';
                    }
                }, 150);
            });
        }
    }
    
    function updateSelection(items, selectedIndex) {
        items.forEach((item, index) => {
            item.classList.toggle('selected', index === selectedIndex);
        });
    }
    
    function performSearch(query, resultsContainer) {
        // Show loading state
        resultsContainer.innerHTML = '<div class="search-result-item text-muted"><i class="fas fa-spinner fa-spin me-2"></i>Searching...</div>';
        resultsContainer.style.display = 'block';
        
        // Use AbortController for request cancellation
        if (window.currentSearchController) {
            window.currentSearchController.abort();
        }
        
        window.currentSearchController = new AbortController();
        
        fetch(`/search/?q=${encodeURIComponent(query)}`, {
            signal: window.currentSearchController.signal,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                displaySearchResults(data.results, resultsContainer);
            })
            .catch(error => {
                if (error.name === 'AbortError') {
                    // Request was cancelled, ignore
                    return;
                }
                console.error('Search error:', error);
                resultsContainer.innerHTML = '<div class="search-result-item text-danger"><i class="fas fa-exclamation-triangle me-2"></i>Search failed. Please try again.</div>';
            });
    }
    
    function displaySearchResults(results, resultsContainer) {
        if (results.length === 0) {
            resultsContainer.innerHTML = '<div class="search-result-item text-muted"><i class="fas fa-search me-2"></i>No results found</div>';
        } else {
            resultsContainer.innerHTML = results.map((item, index) => `
                <div class="search-result-item" data-index="${index}" onclick="navigateToItem('${item.url}')" role="button" tabindex="0">
                    <div class="d-flex align-items-center p-2">
                        ${item.image ? `<img src="${item.image}" alt="${item.name}" class="rounded me-3" style="width: 50px; height: 50px; object-fit: cover; flex-shrink: 0;">` : '<div class="search-item-placeholder me-3"><i class="fas fa-utensils"></i></div>'}
                        <div class="flex-grow-1 min-w-0">
                            <div class="fw-bold text-truncate">${item.name}</div>
                            <div class="text-success small">₹${item.price}</div>
                        </div>
                        <div class="text-muted small">
                            <i class="fas fa-arrow-right"></i>
                        </div>
                    </div>
                </div>
            `).join('');
            
            // Add keyboard event listeners to result items
            const resultItems = resultsContainer.querySelectorAll('.search-result-item');
            resultItems.forEach(item => {
                item.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        this.click();
                    }
                });
            });
        }
        resultsContainer.style.display = 'block';
    }
    
    // Global function to handle navigation
    window.navigateToItem = function(url) {
        if (url) {
            window.location.href = url;
        }
    };
}

// Notification system
function initializeNotifications() {
    window.showNotification = function(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
        
        return notification;
    };
}

// Scroll effects
function initializeScrollEffects() {
    // Navbar background on scroll
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('shadow-sm');
            } else {
                navbar.classList.remove('shadow-sm');
            }
        });
    }
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Fade in animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card, .feature-card').forEach(el => {
        observer.observe(el);
    });
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
}

// Lazy loading for images
function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Utility functions
window.utils = {
    // Format currency
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    },
    
    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle function
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Local storage helpers
    storage: {
        set: function(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.error('Failed to save to localStorage:', e);
            }
        },
        
        get: function(key) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : null;
            } catch (e) {
                console.error('Failed to read from localStorage:', e);
                return null;
            }
        },
        
        remove: function(key) {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                console.error('Failed to remove from localStorage:', e);
            }
        }
    },
    
    // Cookie helpers
    cookies: {
        set: function(name, value, days = 7) {
            const expires = new Date();
            expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
            document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
        },
        
        get: function(name) {
            const nameEQ = name + "=";
            const ca = document.cookie.split(';');
            for (let i = 0; i < ca.length; i++) {
                let c = ca[i];
                while (c.charAt(0) === ' ') c = c.substring(1, c.length);
                if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
            }
            return null;
        },
        
        delete: function(name) {
            document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        }
    }
};

// Cart functionality
window.cart = {
    add: function(itemId, quantity = 1) {
        return fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': window.csrfToken
            },
            body: `menu_item_id=${itemId}&quantity=${quantity}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updateCount(data.cart_count);
                this.showCartNotification(data.message, 'success', data.item_name, data.item_image);
            } else if (data.redirect) {
                // User needs to login
                showNotification(data.message, 'warning');
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1500);
            } else {
                showNotification(data.message || 'Failed to add item to cart', 'danger');
            }
            return data;
        })
        .catch(error => {
            console.error('Cart error:', error);
            showNotification('Failed to add item to cart', 'danger');
        });
    },
    
    showCartNotification: function(message, type, itemName, itemImage) {
        // Create simple toast notification (not modal)
        const notification = document.createElement('div');
        notification.className = `cart-notification alert alert-${type} alert-dismissible fade show`;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            min-width: 320px;
            max-width: 400px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            border-radius: 15px;
            animation: slideInRight 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            border: none;
            background: white;
            color: #333;
        `;
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="flex-shrink-0 me-3">
                    ${itemImage ? 
                        `<img src="${itemImage}" alt="${itemName}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 10px;">` :
                        `<div style="width: 60px; height: 60px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem;">
                            <i class="fas fa-utensils"></i>
                        </div>`
                    }
                </div>
                <div class="flex-grow-1">
                    <div class="d-flex align-items-center mb-1">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        <strong>Added to Cart!</strong>
                    </div>
                    <div class="text-muted small">${itemName || message}</div>
                    <a href="/cart/" class="btn btn-sm btn-primary mt-2" style="border-radius: 8px;">
                        <i class="fas fa-shopping-cart me-1"></i>View Cart
                    </a>
                </div>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()" style="font-size: 0.8rem;"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.add('fade-out');
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
        
        // Add animation styles if not already present
        if (!document.getElementById('cart-notification-styles')) {
            const style = document.createElement('style');
            style.id = 'cart-notification-styles';
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
                .cart-notification.fade-out {
                    animation: fadeOutRight 0.3s ease-out forwards;
                }
                @keyframes fadeOutRight {
                    from {
                        opacity: 1;
                        transform: translateX(0);
                    }
                    to {
                        opacity: 0;
                        transform: translateX(100%);
                    }
                }
                .cart-notification:hover {
                    transform: scale(1.02);
                    transition: transform 0.2s ease;
                }
            `;
            document.head.appendChild(style);
        }
    },
    
    update: function(cartItemId, quantity) {
        return fetch('/cart/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': window.csrfToken
            },
            body: `cart_item_id=${cartItemId}&quantity=${quantity}`
        })
        .then(response => response.json());
    },
    
    remove: function(cartItemId) {
        return fetch('/cart/remove/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': window.csrfToken
            },
            body: `cart_item_id=${cartItemId}`
        })
        .then(response => response.json());
    },
    
    updateCount: function(count) {
        const cartLink = document.querySelector('.cart-link');
        let cartBadge = document.querySelector('.cart-badge');
        
        if (count > 0) {
            if (cartBadge) {
                // Update existing badge
                cartBadge.textContent = count;
                // Animate badge
                cartBadge.style.animation = 'none';
                setTimeout(() => {
                    cartBadge.style.animation = 'pulse 0.6s ease-in-out';
                }, 10);
            } else if (cartLink) {
                // Create new badge if it doesn't exist
                const cartIconContainer = cartLink.querySelector('.cart-icon-container');
                if (cartIconContainer) {
                    const badge = document.createElement('span');
                    badge.className = 'cart-badge';
                    badge.textContent = count;
                    cartIconContainer.appendChild(badge);
                    // Animate new badge
                    setTimeout(() => {
                        badge.style.animation = 'pulse 0.6s ease-in-out';
                    }, 10);
                }
            }
        } else if (cartBadge) {
            // Remove badge if count is 0
            cartBadge.remove();
        }
    }
};

// Performance monitoring
window.performance && window.performance.mark && window.performance.mark('app-initialized');
// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // You could send this to a logging service
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    // You could send this to a logging service
});

// Service Worker registration (for PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Serve service worker from static files
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Mobile optimizations
function initializeMobileOptimizations() {
    // Improve touch interactions on mobile
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
        
        // Add smooth touch feedback to buttons
        const buttons = document.querySelectorAll('.btn, .nav-link, .card');
        buttons.forEach(button => {
            button.addEventListener('touchstart', function() {
                this.style.transition = 'transform 0.1s ease';
                this.style.transform = 'scale(0.98)';
            });
            
            button.addEventListener('touchend', function() {
                this.style.transition = 'transform 0.1s ease';
                this.style.transform = '';
            });
        });
    }
    
    // Initialize mobile search
    initializeMobileSearch();
    
    // Optimize scrolling performance
    let ticking = false;
    function updateScrollEffects() {
        // Your scroll effects here
        ticking = false;
    }
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateScrollEffects);
            ticking = true;
        }
    });
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(function() {
            // Recalculate layouts after orientation change
            window.dispatchEvent(new Event('resize'));
        }, 100);
    });
}

// Mobile Search Overlay
function initializeMobileSearch() {
    const searchToggle = document.getElementById('mobileSearchToggle');
    const searchOverlay = document.getElementById('mobileSearchOverlay');
    const closeSearch = document.getElementById('closeMobileSearch');
    const searchInput = document.getElementById('mobile-search-input');
    const searchForm = document.querySelector('.mobile-search-form');
    const resultsContainer = document.getElementById('mobile-search-results');
    
    if (!searchOverlay) return;
    
    function openSearchOverlay(e) {
        if (e) e.preventDefault();
        searchOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        setTimeout(() => {
            if (searchInput) searchInput.focus();
        }, 300);
    }
    
    if (searchToggle) {
        searchToggle.addEventListener('click', openSearchOverlay);
    }
    
    // Close search overlay
    if (closeSearch) {
        closeSearch.addEventListener('click', function() {
            searchOverlay.classList.remove('active');
            document.body.style.overflow = '';
            if (searchInput) searchInput.value = '';
            if (resultsContainer) resultsContainer.innerHTML = '';
        });
    }
    
    // Close on overlay click
    searchOverlay.addEventListener('click', function(e) {
        if (e.target === searchOverlay) {
            searchOverlay.classList.remove('active');
            document.body.style.overflow = '';
            if (searchInput) searchInput.value = '';
            if (resultsContainer) resultsContainer.innerHTML = '';
        }
    });
    
    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
            searchOverlay.classList.remove('active');
            document.body.style.overflow = '';
            if (searchInput) searchInput.value = '';
            if (resultsContainer) resultsContainer.innerHTML = '';
        }
    });
    
    // Live search as user types
    if (searchInput && resultsContainer) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                resultsContainer.innerHTML = '';
                return;
            }
            
            // Show loading state
            resultsContainer.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--gray-400);"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';
            
            searchTimeout = setTimeout(() => {
                performMobileSearch(query);
            }, 300);
        });
    }
    
    // Handle form submission - prevent default and just use live results
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Results are already shown via live search
        });
    }
}

// Perform mobile search with live results
function performMobileSearch(query) {
    const resultsContainer = document.getElementById('mobile-search-results');
    if (!resultsContainer) return;
    
    // Fetch search results from the API
    fetch(`/menu/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.results && data.results.length > 0) {
                resultsContainer.innerHTML = data.results.map(item => {
                    // Ensure image URL is valid
                    const imageUrl = item.image || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop';
                    
                    return `
                        <a href="/menu/item/${item.slug}/" class="search-result-item">
                            <img src="${imageUrl}" 
                                 alt="${item.name}" 
                                 class="search-result-image" 
                                 onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop';">
                            <div class="search-result-info">
                                <span class="search-result-name">${item.name}</span>
                                <small class="search-result-category" style="display: block; color: var(--gray-500); font-size: 0.8rem; margin-bottom: 0.2rem;">${item.category}</small>
                                <span class="search-result-price">₹${item.price}</span>
                            </div>
                        </a>
                    `;
                }).join('');
            } else {
                resultsContainer.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: var(--gray-400);">
                        <i class="fas fa-search" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                        <p style="margin: 0;">No items found for "${query}"</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Search error:', error);
            resultsContainer.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--danger-color);">
                    <i class="fas fa-exclamation-circle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                    <p style="margin: 0;">Search failed. Please try again.</p>
                </div>
            `;
        });
}

// Mobile Sidebar Initialization (Removed - using dropdown instead)
function initializeMobileSidebar() {
    // Mobile sidebar removed - now using dropdown menu
    // Dropdown is handled by Bootstrap automatically
    console.log('Mobile navigation using dropdown menu');
}


// Mobile Sidebar Navigation
function initializeMobileSidebar() {
    const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');
    const mobileSidebar = document.getElementById('mobileSidebar');
    const mobileSidebarOverlay = document.getElementById('mobileSidebarOverlay');
    const mobileSidebarClose = document.getElementById('mobileSidebarClose');

    // Debug logging
    console.log('Mobile sidebar elements:', {
        toggle: !!mobileSidebarToggle,
        sidebar: !!mobileSidebar,
        overlay: !!mobileSidebarOverlay,
        close: !!mobileSidebarClose
    });

    if (mobileSidebarToggle && mobileSidebar && mobileSidebarOverlay) {
        // Open sidebar
        mobileSidebarToggle.addEventListener('click', function(e) {
            console.log('Mobile sidebar toggle clicked');
            e.preventDefault();
            e.stopPropagation();
            
            // Add active classes with force
            mobileSidebar.classList.add('active');
            mobileSidebarOverlay.classList.add('active');
            document.body.classList.add('sidebar-open');
            
            // Prevent body scroll
            document.body.style.overflow = 'hidden';
            document.body.style.position = 'fixed';
            document.body.style.width = '100%';
            
            // Force reflow to ensure animation works
            mobileSidebar.offsetHeight;
            
            // Debug: Check if classes were added
            console.log('Sidebar classes after opening:', mobileSidebar.className);
            console.log('Overlay classes after opening:', mobileSidebarOverlay.className);
        });

        // Close sidebar function
        function closeSidebar() {
            console.log('Closing mobile sidebar');
            mobileSidebar.classList.remove('active');
            mobileSidebarOverlay.classList.remove('active');
            document.body.classList.remove('sidebar-open');
            
            // Restore body scroll
            document.body.style.overflow = '';
            document.body.style.position = '';
            document.body.style.width = '';
        }

        // Close sidebar on close button click
        if (mobileSidebarClose) {
            mobileSidebarClose.addEventListener('click', function(e) {
                console.log('Mobile sidebar close button clicked');
                e.preventDefault();
                e.stopPropagation();
                closeSidebar();
            });
        }

        // Close sidebar on overlay click
        mobileSidebarOverlay.addEventListener('click', function(e) {
            console.log('Mobile sidebar overlay clicked');
            if (e.target === mobileSidebarOverlay) {
                e.preventDefault();
                closeSidebar();
            }
        });

        // Close sidebar on link click
        const mobileNavLinks = mobileSidebar.querySelectorAll('.mobile-nav-link');
        console.log('Found mobile nav links:', mobileNavLinks.length);
        mobileNavLinks.forEach((link, index) => {
            link.addEventListener('click', function(e) {
                console.log('Mobile nav link clicked:', index);
                // Don't close immediately for forms (logout button)
                if (this.tagName.toLowerCase() !== 'button') {
                    setTimeout(closeSidebar, 200);
                }
            });
        });

        // Close sidebar on ESC key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && mobileSidebar.classList.contains('active')) {
                console.log('ESC key pressed, closing sidebar');
                closeSidebar();
            }
        });

        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 992 && mobileSidebar.classList.contains('active')) {
                closeSidebar();
            }
        });

        // Prevent sidebar content from closing sidebar when clicked
        const sidebarContent = mobileSidebar.querySelector('.mobile-sidebar-content');
        if (sidebarContent) {
            sidebarContent.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }

        // Add touch support for better mobile experience
        let startX = 0;
        let currentX = 0;
        let isDragging = false;

        mobileSidebar.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
            isDragging = true;
        });

        mobileSidebar.addEventListener('touchmove', function(e) {
            if (!isDragging) return;
            currentX = e.touches[0].clientX;
            const diffX = startX - currentX;
            
            if (diffX > 0) {
                // Dragging left (closing)
                const translateX = Math.min(diffX, 300);
                mobileSidebar.style.transform = `translateX(-${translateX}px)`;
            }
        });

        mobileSidebar.addEventListener('touchend', function(e) {
            if (!isDragging) return;
            isDragging = false;
            
            const diffX = startX - currentX;
            mobileSidebar.style.transform = '';
            
            if (diffX > 100) {
                // Close if dragged more than 100px
                closeSidebar();
            }
        });

    } else {
        console.error('Mobile sidebar elements not found:', {
            toggle: mobileSidebarToggle,
            sidebar: mobileSidebar,
            overlay: mobileSidebarOverlay
        });
    }
}

