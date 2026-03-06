/**
 * Responsive Web Design Utilities
 * Handles responsive behavior, breakpoints, and dynamic viewport adjustments
 * Version: 1.0
 */

class ResponsiveManager {
    constructor() {
        this.breakpoints = {
            xs: 0,
            sm: 576,
            md: 768,
            lg: 992,
            xl: 1200,
            xxl: 1400
        };
        this.currentBreakpoint = this.getCurrentBreakpoint();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.handleViewportChanges();
        this.detectTouchDevice();
        this.optimizeImages();
        this.handleResponsiveNavigation();
    }

    /**
     * Get current breakpoint based on window width
     */
    getCurrentBreakpoint() {
        const width = window.innerWidth;
        if (width >= this.breakpoints.xxl) return 'xxl';
        if (width >= this.breakpoints.xl) return 'xl';
        if (width >= this.breakpoints.lg) return 'lg';
        if (width >= this.breakpoints.md) return 'md';
        if (width >= this.breakpoints.sm) return 'sm';
        return 'xs';
    }

    /**
     * Check if we're at a specific breakpoint
     */
    isBreakpoint(name) {
        return this.getCurrentBreakpoint() === name;
    }

    /**
     * Check if viewport is at or above a breakpoint
     */
    isBreakpointAndUp(name) {
        const breakpoints = Object.keys(this.breakpoints);
        const currentIndex = breakpoints.indexOf(this.currentBreakpoint);
        const targetIndex = breakpoints.indexOf(name);
        return currentIndex >= targetIndex;
    }

    /**
     * Check if viewport is below a breakpoint
     */
    isBreakpointBelow(name) {
        return !this.isBreakpointAndUp(name);
    }

    /**
     * Setup viewport change listeners
     */
    setupEventListeners() {
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                const newBreakpoint = this.getCurrentBreakpoint();
                if (newBreakpoint !== this.currentBreakpoint) {
                    this.currentBreakpoint = newBreakpoint;
                    this.dispatchBreakpointChangeEvent();
                    this.onBreakpointChange();
                }
            }, 250); // Debounce resize events
        });

        // Detect orientation change
        window.addEventListener('orientationchange', () => {
            this.handleOrientationChange();
        });
    }

    /**
     * Dispatch custom event when breakpoint changes
     */
    dispatchBreakpointChangeEvent() {
        const event = new CustomEvent('breakpointChange', {
            detail: { breakpoint: this.currentBreakpoint }
        });
        window.dispatchEvent(event);
    }

    /**
     * Handle breakpoint changes
     */
    onBreakpointChange() {
        // Update navbar
        this.updateNavigationLayout();
        
        // Update layout-specific elements
        this.updateGridLayout();
        
        // Adjust content
        this.adjustContentLayout();
    }

    /**
     * Handle orientation changes
     */
    handleOrientationChange() {
        const orientation = window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
        document.body.classList.add(`orientation-${orientation}`);
        
        // Prevent zoom on orientation change
        const viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {
            viewport.setAttribute('content', 'width=device-width, initial-scale=1, viewport-fit=cover');
        }
    }

    /**
     * Handle viewport changes
     */
    handleViewportChanges() {
        // Ensure proper viewport meta tag
        const viewport = document.querySelector('meta[name="viewport"]');
        if (!viewport) {
            const meta = document.createElement('meta');
            meta.name = 'viewport';
            meta.content = 'width=device-width, initial-scale=1, viewport-fit=cover, maximum-scale=5';
            document.head.appendChild(meta);
        }

        // Mobile safe area adjustments
        this.adjustSafeAreas();
    }

    /**
     * Adjust for safe areas (notches, etc.)
     */
    adjustSafeAreas() {
        const docStyle = document.documentElement.style;
        
        if (CSS.supports('padding', 'max(0px)')) {
            // Use env() for safe area insets
            docStyle.setProperty('--safe-area-inset-top', 'env(safe-area-inset-top, 0)');
            docStyle.setProperty('--safe-area-inset-left', 'env(safe-area-inset-left, 0)');
            docStyle.setProperty('--safe-area-inset-right', 'env(safe-area-inset-right, 0)');
            docStyle.setProperty('--safe-area-inset-bottom', 'env(safe-area-inset-bottom, 0)');
        }
    }

    /**
     * Update navigation layout based on breakpoint
     */
    updateNavigationLayout() {
        const navbar = document.querySelector('.main-navbar');
        const mobileNav = document.querySelector('.mobile-bottom-nav');

        if (!navbar || !mobileNav) return;

        if (this.isBreakpointBelow('lg')) {
            // Mobile navigation
            mobileNav.style.display = 'flex';
            this.optimizeMobileNav();
        } else {
            // Desktop navigation
            mobileNav.style.display = 'none';
        }
    }

    /**
     * Optimize mobile navigation
     */
    optimizeMobileNav() {
        const mobileNav = document.querySelector('.mobile-bottom-nav');
        if (!mobileNav) return;

        // Enable touch optimizations
        mobileNav.classList.add('touch-optimized');
    }

    /**
     * Update grid layouts responsively
     */
    updateGridLayout() {
        const grids = document.querySelectorAll('[class*="grid-"]');
        
        grids.forEach(grid => {
            if (this.isBreakpointBelow('md')) {
                // Stack on mobile
                grid.style.gridTemplateColumns = '1fr';
            } else if (grid.classList.contains('grid-2')) {
                grid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(300px, 1fr))';
            } else if (grid.classList.contains('grid-3')) {
                grid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(250px, 1fr))';
            } else if (grid.classList.contains('grid-4')) {
                grid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(200px, 1fr))';
            }
        });
    }

    /**
     * Adjust content layout
     */
    adjustContentLayout() {
        const containers = document.querySelectorAll('.container, .container-fluid');
        
        containers.forEach(container => {
            if (this.isBreakpointBelow('sm')) {
                container.style.paddingLeft = '0.75rem';
                container.style.paddingRight = '0.75rem';
            } else if (this.isBreakpointBelow('md')) {
                container.style.paddingLeft = '1rem';
                container.style.paddingRight = '1rem';
            } else if (this.isBreakpointBelow('lg')) {
                container.style.paddingLeft = '1.5rem';
                container.style.paddingRight = '1.5rem';
            } else {
                container.style.paddingLeft = '2rem';
                container.style.paddingRight = '2rem';
            }
        });
    }

    /**
     * Detect if device is touch-capable
     */
    detectTouchDevice() {
        const isTouchDevice = () => {
            return (
                (typeof window !== 'undefined' &&
                    ('ontouchstart' in window ||
                        navigator.maxTouchPoints > 0 ||
                        navigator.msMaxTouchPoints > 0)) ||
                (typeof window !== 'undefined' && window.DocumentTouch && document instanceof window.DocumentTouch)
            );
        };

        if (isTouchDevice()) {
            document.body.classList.add('touch-device');
            this.optimizeTouchInteractions();
        } else {
            document.body.classList.add('non-touch-device');
        }
    }

    /**
     * Optimize for touch interactions
     */
    optimizeTouchInteractions() {
        // Remove hover effects and use active states instead
        const style = document.createElement('style');
        style.textContent = `
            @media (hover: none) and (pointer: coarse) {
                button:hover,
                a:hover,
                .btn:hover {
                    opacity: 1;
                    transform: none;
                }
                
                button:active,
                a:active,
                .btn:active {
                    opacity: 0.8;
                    transform: scale(0.98);
                }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Optimize images for responsive loading
     */
    optimizeImages() {
        const images = document.querySelectorAll('img:not([loading])');
        
        images.forEach(img => {
            // Set loading attribute for native lazy loading
            img.attribut = 'lazy';
            
            // Ensure images are responsive
            if (!img.style.maxWidth) {
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
                img.style.display = 'block';
            }
        });

        // Implement intersection observer for lazy loading
        this.setupLazyLoading();
    }

    /**
     * Setup lazy loading for images
     */
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                        }
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px'
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    /**
     * Handle responsive navigation
     */
    handleResponsiveNavigation() {
        // Mobile search toggle
        const mobileSearchToggle = document.getElementById('mobileSearchToggle');
        if (mobileSearchToggle) {
            mobileSearchToggle.addEventListener('click', () => {
                this.toggleMobileSearch();
            });
        }

        // Close mobile search when clicking outside
        document.addEventListener('click', (e) => {
            const searchOverlay = document.querySelector('.mobile-search-overlay');
            if (searchOverlay && searchOverlay.classList.contains('active')) {
                if (!e.target.closest('.mobile-search-overlay') && 
                    !e.target.closest('#mobileSearchToggle')) {
                    searchOverlay.classList.remove('active');
                }
            }
        });
    }

    /**
     * Toggle mobile search
     */
    toggleMobileSearch() {
        const overlay = document.querySelector('.mobile-search-overlay');
        if (overlay) {
            overlay.classList.toggle('active');
            if (overlay.classList.contains('active')) {
                const input = overlay.querySelector('.mobile-search-input');
                if (input) {
                    setTimeout(() => input.focus(), 100);
                }
            }
        }
    }

    /**
     * Get viewport dimensions
     */
    getViewportDimensions() {
        return {
            width: window.innerWidth,
            height: window.innerHeight,
            breakpoint: this.currentBreakpoint
        };
    }

    /**
     * Check if in mobile view
     */
    isMobileView() {
        return this.isBreakpointBelow('lg');
    }

    /**
     * Check if in tablet view
     */
    isTabletView() {
        return this.isBreakpointAndUp('md') && this.isBreakpointBelow('lg');
    }

    /**
     * Check if in desktop view
     */
    isDesktopView() {
        return this.isBreakpointAndUp('lg');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.responsiveManager = new ResponsiveManager();
    });
} else {
    window.responsiveManager = new ResponsiveManager();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ResponsiveManager;
}
