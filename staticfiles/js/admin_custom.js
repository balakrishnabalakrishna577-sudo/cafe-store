// Admin sidebar functionality with proper toggle support
document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;
    const sidebar = document.querySelector('.main-sidebar');
    const contentWrapper = document.querySelector('.content-wrapper');
    const sidebarToggle = document.querySelector('[data-widget="pushmenu"]');
    
    // Initialize sidebar styles
    function initSidebar() {
        if (sidebar) {
            sidebar.style.overflowY = 'auto';
            sidebar.style.overflowX = 'hidden';
            sidebar.style.height = '100vh';
            sidebar.style.position = 'fixed';
        }
        
        const sidebarContainer = document.querySelector('.sidebar');
        if (sidebarContainer) {
            sidebarContainer.style.overflowY = 'auto';
            sidebarContainer.style.overflowX = 'hidden';
            sidebarContainer.style.height = '100%';
            sidebarContainer.style.paddingBottom = '20px';
        }
        
        const osHost = document.querySelector('.os-host');
        if (osHost) {
            osHost.style.overflowY = 'auto';
            osHost.style.height = '100%';
        }
        
        const osHostOverflow = document.querySelector('.os-host-overflow');
        if (osHostOverflow) {
            osHostOverflow.style.overflowY = 'auto';
            osHostOverflow.style.height = '100%';
        }
    }
    
    // Update content wrapper margin based on sidebar state
    function updateContentMargin() {
        if (contentWrapper) {
            if (body.classList.contains('sidebar-collapse')) {
                // Sidebar collapsed
                contentWrapper.style.marginLeft = '0';
            } else {
                // Sidebar expanded
                contentWrapper.style.marginLeft = '280px';
            }
        }
    }
    
    // Initialize
    initSidebar();
    
    // Start with sidebar open on desktop, collapsed on mobile
    if (window.innerWidth >= 768) {
        body.classList.remove('sidebar-collapse');
        body.classList.add('sidebar-open');
    } else {
        body.classList.add('sidebar-collapse');
        body.classList.remove('sidebar-open');
    }
    
    updateContentMargin();
    
    // Listen for sidebar toggle clicks
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            // Wait for AdminLTE to toggle classes, then update margin
            setTimeout(updateContentMargin, 50);
        });
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 768) {
            // Desktop: keep current state (allow toggle)
            updateContentMargin();
        } else {
            // Mobile: collapse sidebar when resizing to mobile
            if (!body.classList.contains('sidebar-collapse')) {
                body.classList.add('sidebar-collapse');
                body.classList.remove('sidebar-open');
                updateContentMargin();
            }
        }
    });
    
    // Show all text labels
    const navLinks = document.querySelectorAll('.nav-sidebar .nav-link p');
    navLinks.forEach(function(p) {
        p.style.display = 'inline-block';
        p.style.opacity = '1';
        p.style.visibility = 'visible';
        p.style.width = 'auto';
        p.style.marginLeft = '8px';
    });
    
    // Show brand text
    const brandText = document.querySelector('.brand-text');
    if (brandText) {
        brandText.style.display = 'inline-block';
        brandText.style.opacity = '1';
        brandText.style.visibility = 'visible';
    }
    
    // Ensure sidebar is scrollable after a short delay (for dynamic content)
    setTimeout(function() {
        initSidebar();
    }, 500);
});
