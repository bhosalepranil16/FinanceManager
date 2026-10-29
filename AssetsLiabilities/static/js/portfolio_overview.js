// Portfolio Overview - Sidebar Toggle Functionality (jQuery)

/**
 * Toggle sidebar collapsed/expanded state
 */
function toggleSidebar() {
    $('#sidebar').toggleClass('collapsed');
    $('#mainContent').toggleClass('expanded');
    $('#sidebarToggle').toggleClass('collapsed');
    
    // Save state to localStorage
    const isCollapsed = $('#sidebar').hasClass('collapsed');
    localStorage.setItem('sidebarCollapsed', isCollapsed);
}

// Document ready - Initialize sidebar state
$(document).ready(function() {
    // Bind sidebar toggle button
    $('#sidebarToggle').on('click', toggleSidebar);
    
    // Restore sidebar state on page load
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed) {
        $('#sidebar').addClass('collapsed');
        $('#mainContent').addClass('expanded');
        $('#sidebarToggle').addClass('collapsed');
    }
    
    // Handle responsive sidebar on mobile
    if ($(window).width() <= 768) {
        // Start collapsed on mobile
        $('#sidebar').removeClass('active');
    }
});
