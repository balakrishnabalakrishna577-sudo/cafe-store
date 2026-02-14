/**
 * Enhanced User Features JavaScript
 * Provides smooth functionality for all user pages in the cafe delivery system
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all enhanced features
    initializeProfileFeatures();
    initializeOrderFeatures();
    initializeWishlistFeatures();
    initializeCartFeatures();
    initializeNotificationFeatures();
    initializeFormEnhancements();
    initializeAnimations();
});

// ==================== PROFILE FEATURES ====================

function initializeProfileFeatures() {
    // Profile completion progress animation
    animateProgressBars();
    
    // Profile image upload preview
    const profileImageInput = document.getElementById('profile_image');
    if (profileImageInput) {
        profileImageInput.addEventListener('change', previewProfileImage);
    }
    
    // Location detection
    const detectLocationBtn = document.getElementById('detectLocationBtn');
    if (detectLocationBtn) {
        detectLocationBtn.addEventListener('click', detectUserLocation);
    }
    
    // Profile form auto-save
    initializeAutoSave();
}

function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.transition = 'width 1.5s ease-in-out';
            bar.style.width = width;
        }, 500);
    });
}

function previewProfileImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.querySelector('.profile-avatar img') || 
                           document.querySelector('.user-profile-img');
            if (preview) {
                if (preview.tagName === 'IMG') {
                    preview.src = e.target.result;
                } else {
                    preview.innerHTML = `<img src="${e.target.result}" alt="Profile Preview" style="width: 100%; height: 100%; object-fit: cover; border-radius: inherit;">`;
                }
            }
        };
        reader.readAsDataURL(file);
    }
}

function detectUserLocation() {
    const statusDiv = document.getElementById('locationStatus');
    const statusText = document.getElementById('locationStatusText');
    
    if (!navigator.geolocation) {
        showNotification('Geolocation is not supported by this browser.', 'error');
        return;
    }
    
    statusDiv.classList.remove('d-none');
    statusText.textContent = 'Detecting your location...';
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            // Reverse geocoding (you can integrate with Google Maps API or similar)
            statusText.innerHTML = '<i class="fas fa-check-circle me-2"></i>Location detected successfully!';
            statusDiv.className = 'alert alert-success';
            
            // Auto-fill address fields if available
            fillAddressFields(lat, lng);
            
            setTimeout(() => {
                statusDiv.classList.add('d-none');
            }, 3000);
        },
        function(error) {
            let errorMessage = 'Unable to detect location.';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage = 'Location access denied by user.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage = 'Location information is unavailable.';
                    break;
                case error.TIMEOUT:
                    errorMessage = 'Location request timed out.';
                    break;
            }
            
            statusText.innerHTML = `<i class="fas fa-exclamation-circle me-2"></i>${errorMessage}`;
            statusDiv.className = 'alert alert-danger';
            
            setTimeout(() => {
                statusDiv.classList.add('d-none');
            }, 5000);
        }
    );
}

function fillAddressFields(lat, lng) {
    // This would integrate with a geocoding service
    // For now, just show coordinates
    const addressField = document.querySelector('input[name="address"]');
    if (addressField) {
        addressField.value = `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`;
    }
}

function initializeAutoSave() {
    const profileForm = document.getElementById('profileForm');
    if (!profileForm) return;
    
    const inputs = profileForm.querySelectorAll('input, textarea, select');
    let autoSaveTimeout;
    
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                autoSaveProfile();
            }, 2000); // Auto-save after 2 seconds of inactivity
        });
    });
}

function autoSaveProfile() {
    const profileForm = document.getElementById('profileForm');
    if (!profileForm) return;
    
    const formData = new FormData(profileForm);
    formData.append('auto_save', 'true');
    
    fetch(profileForm.action || window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMiniNotification('Profile auto-saved', 'success');
        }
    })
    .catch(error => {
        console.log('Auto-save failed:', error);
    });
}

// ==================== ORDER FEATURES ====================

function initializeOrderFeatures() {
    // Order tracking updates
    initializeOrderTracking();
    
    // Reorder functionality
    const reorderBtns = document.querySelectorAll('[onclick*="reorderItems"]');
    reorderBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const orderNumber = this.getAttribute('data-order') || 
                               this.getAttribute('onclick').match(/'([^']+)'/)[1];
            reorderItems(orderNumber);
        });
    });
    
    // Order filtering and search
    initializeOrderFilters();
}

function initializeOrderTracking() {
    const orderCards = document.querySelectorAll('[data-order-status]');
    orderCards.forEach(card => {
        const status = card.getAttribute('data-order-status');
        if (['pending', 'confirmed', 'preparing', 'out_for_delivery'].includes(status)) {
            // Simulate real-time updates (in production, use WebSockets)
            setTimeout(() => {
                updateOrderStatus(card);
            }, Math.random() * 10000 + 5000);
        }
    });
}

function updateOrderStatus(orderCard) {
    // This would connect to real-time order updates
    const statusBadge = orderCard.querySelector('.badge');
    const progressBar = orderCard.querySelector('.progress-bar');
    
    if (statusBadge && progressBar) {
        // Animate status change
        statusBadge.style.animation = 'pulse 0.5s ease-in-out';
        progressBar.style.transition = 'width 1s ease-in-out';
    }
}

function reorderItems(orderNumber) {
    showConfirm(
        'Reorder Items',
        'Add all items from this order to your cart?',
        () => {
            fetch(`/orders/${orderNumber}/reorder/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Items added to cart successfully!', 'success');
                    updateCartCount(data.cart_count);
                    
                    // Animate the button
                    const btn = document.querySelector(`[onclick*="${orderNumber}"]`);
                    if (btn) {
                        btn.innerHTML = '<i class="fas fa-check me-1"></i>Added!';
                        btn.classList.add('btn-success');
                        setTimeout(() => {
                            btn.innerHTML = '<i class="fas fa-redo me-1"></i>Reorder';
                            btn.classList.remove('btn-success');
                        }, 2000);
                    }
                } else {
                    showNotification('Failed to add items to cart', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Failed to add items to cart', 'error');
            });
        }
    );
}

function initializeOrderFilters() {
    const filterBtns = document.querySelectorAll('.order-filter-btn');
    const searchInput = document.getElementById('orderSearch');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            filterOrders(filter);
            
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(searchOrders, 300));
    }
}

function filterOrders(filter) {
    const orderCards = document.querySelectorAll('.order-card');
    orderCards.forEach(card => {
        const status = card.getAttribute('data-order-status');
        if (filter === 'all' || status === filter) {
            card.style.display = 'block';
            card.style.animation = 'fadeIn 0.3s ease-in-out';
        } else {
            card.style.display = 'none';
        }
    });
}

function searchOrders(query) {
    const orderCards = document.querySelectorAll('.order-card');
    const searchTerm = query.target.value.toLowerCase();
    
    orderCards.forEach(card => {
        const orderNumber = card.querySelector('.order-number')?.textContent.toLowerCase() || '';
        const items = card.querySelector('.order-items')?.textContent.toLowerCase() || '';
        
        if (orderNumber.includes(searchTerm) || items.includes(searchTerm)) {
            card.style.display = 'block';
            card.style.animation = 'fadeIn 0.3s ease-in-out';
        } else {
            card.style.display = 'none';
        }
    });
}

// ==================== WISHLIST FEATURES ====================

function initializeWishlistFeatures() {
    // Wishlist toggle animations
    const wishlistBtns = document.querySelectorAll('.wishlist-btn');
    wishlistBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleWishlist(this);
        });
    });
    
    // Bulk wishlist actions
    initializeBulkWishlistActions();
}

function toggleWishlist(btn) {
    const menuItemId = btn.getAttribute('data-item-id');
    const isInWishlist = btn.classList.contains('in-wishlist');
    
    // Animate button
    btn.style.transform = 'scale(0.8)';
    btn.style.transition = 'all 0.2s ease';
    
    fetch('/toggle-wishlist/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
        },
        body: `menu_item_id=${menuItemId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update button state
            if (data.added) {
                btn.classList.add('in-wishlist');
                btn.innerHTML = '<i class="fas fa-heart"></i>';
                btn.style.color = '#e53e3e';
            } else {
                btn.classList.remove('in-wishlist');
                btn.innerHTML = '<i class="far fa-heart"></i>';
                btn.style.color = '#718096';
            }
            
            // Reset animation
            setTimeout(() => {
                btn.style.transform = 'scale(1)';
            }, 200);
            
            showMiniNotification(data.message, 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        btn.style.transform = 'scale(1)';
    });
}

function initializeBulkWishlistActions() {
    const selectAllBtn = document.getElementById('selectAllWishlist');
    const bulkActionBtns = document.querySelectorAll('.bulk-action-btn');
    
    if (selectAllBtn) {
        selectAllBtn.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.wishlist-item-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBulkActionButtons();
        });
    }
    
    bulkActionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const selectedItems = getSelectedWishlistItems();
            
            if (selectedItems.length === 0) {
                showNotification('Please select items first', 'warning');
                return;
            }
            
            performBulkWishlistAction(action, selectedItems);
        });
    });
}

// ==================== CART FEATURES ====================

function initializeCartFeatures() {
    // Quantity controls
    const quantityBtns = document.querySelectorAll('.quantity-btn');
    quantityBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const itemId = this.getAttribute('data-item-id');
            updateQuantity(itemId, action);
        });
    });
    
    // Cart item selection
    const itemSelectors = document.querySelectorAll('.item-selector');
    itemSelectors.forEach(selector => {
        selector.addEventListener('change', updateCartSelection);
    });
    
    // Coupon functionality
    initializeCouponFeatures();
}

function updateQuantity(itemId, action) {
    const quantityInput = document.querySelector(`input[data-item-id="${itemId}"]`);
    let currentQuantity = parseInt(quantityInput.value);
    
    if (action === 'increase') {
        currentQuantity++;
    } else if (action === 'decrease' && currentQuantity > 1) {
        currentQuantity--;
    }
    
    quantityInput.value = currentQuantity;
    
    // Update cart via AJAX
    fetch('/update-cart-quantity/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
        },
        body: `item_id=${itemId}&quantity=${currentQuantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update item total
            const itemTotal = document.querySelector(`[data-item-id="${itemId}"] .item-total`);
            if (itemTotal) {
                itemTotal.textContent = `₹${data.item_total}`;
            }
            
            // Update cart totals
            updateCartTotals(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Revert quantity on error
        quantityInput.value = action === 'increase' ? currentQuantity - 1 : currentQuantity + 1;
    });
}

function updateCartSelection() {
    const selectedItems = document.querySelectorAll('.item-selector:checked').length;
    const checkoutBtn = document.getElementById('proceedToCheckout');
    
    if (checkoutBtn) {
        if (selectedItems > 0) {
            checkoutBtn.disabled = false;
            checkoutBtn.innerHTML = `<i class="fas fa-credit-card me-2"></i>Proceed to Checkout (${selectedItems})`;
        } else {
            checkoutBtn.disabled = true;
            checkoutBtn.innerHTML = '<i class="fas fa-lock me-2"></i>Select items to checkout';
        }
    }
}

function initializeCouponFeatures() {
    const couponForm = document.getElementById('couponForm');
    const couponInput = document.getElementById('couponCode');
    
    if (couponForm) {
        couponForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyCoupon();
        });
    }
    
    if (couponInput) {
        couponInput.addEventListener('input', debounce(validateCoupon, 500));
    }
}

function applyCoupon() {
    const couponCode = document.getElementById('couponCode').value.trim();
    const applyBtn = document.getElementById('applyBtn');
    const originalText = applyBtn.innerHTML;
    
    if (!couponCode) {
        showNotification('Please enter a coupon code', 'warning');
        return;
    }
    
    applyBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Applying...';
    applyBtn.disabled = true;
    
    fetch('/apply-coupon/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
        },
        body: `coupon_code=${couponCode}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAppliedCoupon(data.coupon);
            updateCartTotals(data);
            showNotification('Coupon applied successfully!', 'success');
        } else {
            showNotification(data.message || 'Invalid coupon code', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Failed to apply coupon', 'error');
    })
    .finally(() => {
        applyBtn.innerHTML = originalText;
        applyBtn.disabled = false;
    });
}

// ==================== NOTIFICATION FEATURES ====================

function initializeNotificationFeatures() {
    // Mark notifications as read
    const notifications = document.querySelectorAll('.notification-item');
    notifications.forEach(notification => {
        notification.addEventListener('click', function() {
            markNotificationAsRead(this);
        });
    });
    
    // Real-time notifications (would use WebSockets in production)
    initializeRealTimeNotifications();
}

function markNotificationAsRead(notificationElement) {
    const notificationId = notificationElement.getAttribute('data-notification-id');
    
    if (notificationElement.classList.contains('unread')) {
        fetch(`/mark-notification-read/${notificationId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                notificationElement.classList.remove('unread');
                updateNotificationCount();
            }
        });
    }
}

function initializeRealTimeNotifications() {
    // Simulate real-time notifications
    setInterval(() => {
        checkForNewNotifications();
    }, 30000); // Check every 30 seconds
}

function checkForNewNotifications() {
    fetch('/check-notifications/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.new_notifications > 0) {
            updateNotificationCount(data.total_unread);
            showMiniNotification(`You have ${data.new_notifications} new notification(s)`, 'info');
        }
    })
    .catch(error => {
        console.log('Notification check failed:', error);
    });
}

// ==================== FORM ENHANCEMENTS ====================

function initializeFormEnhancements() {
    // Form validation
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
    
    // Input formatting
    initializeInputFormatting();
    
    // File upload enhancements
    initializeFileUploads();
}

function validateForm(e) {
    const form = e.target;
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    if (!isValid) {
        e.preventDefault();
        showNotification('Please fill in all required fields', 'error');
    }
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error text-danger small mt-1';
    errorDiv.textContent = message;
    
    field.classList.add('is-invalid');
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function initializeInputFormatting() {
    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', formatPhoneNumber);
    });
    
    // Currency formatting
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(input => {
        input.addEventListener('input', formatCurrency);
    });
}

function formatPhoneNumber(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length >= 10) {
        value = value.substring(0, 10);
        value = value.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
    }
    e.target.value = value;
}

function formatCurrency(e) {
    let value = e.target.value.replace(/[^\d.]/g, '');
    if (value) {
        value = parseFloat(value).toLocaleString('en-IN', {
            style: 'currency',
            currency: 'INR'
        });
    }
    e.target.value = value;
}

// ==================== ANIMATIONS ====================

function initializeAnimations() {
    // Scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    animateElements.forEach(el => observer.observe(el));
    
    // Loading animations
    initializeLoadingAnimations();
}

function initializeLoadingAnimations() {
    // Button loading states
    const submitBtns = document.querySelectorAll('button[type="submit"]');
    submitBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.form && this.form.checkValidity()) {
                showButtonLoading(this);
            }
        });
    });
}

function showButtonLoading(btn) {
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    btn.disabled = true;
    
    // Reset after 5 seconds (fallback)
    setTimeout(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }, 5000);
}

// ==================== UTILITY FUNCTIONS ====================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function updateCartCount(count) {
    const cartBadges = document.querySelectorAll('.cart-badge');
    cartBadges.forEach(badge => {
        badge.textContent = count;
        if (count > 0) {
            badge.style.display = 'inline-block';
            badge.style.animation = 'pulse 0.5s ease-in-out';
        } else {
            badge.style.display = 'none';
        }
    });
}

function updateNotificationCount(count) {
    const notificationBadges = document.querySelectorAll('.notification-badge');
    notificationBadges.forEach(badge => {
        if (count && count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    });
}

function showMiniNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `mini-notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : 'info'}-circle me-2"></i>
        ${message}
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${type === 'success' ? '#48bb78' : type === 'error' ? '#f56565' : '#4299e1'};
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        font-size: 0.875rem;
        font-weight: 500;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function updateCartTotals(data) {
    // Update various total elements
    const elements = {
        '.subtotal-amount': data.subtotal,
        '.delivery-amount': data.delivery_fee,
        '.total-amount': data.total,
        '.discount-amount': data.discount
    };
    
    Object.entries(elements).forEach(([selector, value]) => {
        const element = document.querySelector(selector);
        if (element && value !== undefined) {
            element.textContent = `₹${value}`;
        }
    });
}

function showAppliedCoupon(coupon) {
    const appliedCouponDiv = document.getElementById('appliedCoupon');
    const couponCodeSpan = document.getElementById('appliedCouponCode');
    const couponDescSpan = document.getElementById('couponDescription');
    
    if (appliedCouponDiv && couponCodeSpan) {
        couponCodeSpan.textContent = coupon.code;
        if (couponDescSpan) {
            couponDescSpan.textContent = coupon.description;
        }
        appliedCouponDiv.style.display = 'block';
        
        // Hide coupon form
        const couponForm = document.getElementById('couponForm');
        if (couponForm) {
            couponForm.style.display = 'none';
        }
    }
}

function removeCoupon() {
    fetch('/remove-coupon/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hide applied coupon
            const appliedCouponDiv = document.getElementById('appliedCoupon');
            if (appliedCouponDiv) {
                appliedCouponDiv.style.display = 'none';
            }
            
            // Show coupon form
            const couponForm = document.getElementById('couponForm');
            if (couponForm) {
                couponForm.style.display = 'block';
                document.getElementById('couponCode').value = '';
            }
            
            updateCartTotals(data);
            showNotification('Coupon removed', 'info');
        }
    });
}

// Global notification function (if not already defined)
if (typeof showNotification === 'undefined') {
    window.showNotification = function(message, type = 'info') {
        showMiniNotification(message, type);
    };
}

// Global confirm function (if not already defined)
if (typeof showConfirm === 'undefined') {
    window.showConfirm = function(title, message, onConfirm, confirmText = 'Confirm', cancelText = 'Cancel') {
        if (confirm(`${title}\n\n${message}`)) {
            onConfirm();
        }
    };
}

console.log('Enhanced User Features initialized successfully!');