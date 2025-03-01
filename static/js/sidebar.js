document.addEventListener('DOMContentLoaded', function() {
    // Get necessary elements
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('main') || document.querySelector('.main-content');
    
    // Create toggle button for mobile
    const toggleButton = document.createElement('button');
    toggleButton.className = 'sidebar-toggle';
    toggleButton.innerHTML = '<i class="fas fa-bars"></i>';
    toggleButton.setAttribute('aria-label', 'Toggle Sidebar');
    
    // Insert the toggle button at the top of the page (you may want to adjust this location)
    document.body.insertBefore(toggleButton, document.body.firstChild);
    
    // Add CSS for mobile styling
    const style = document.createElement('style');
    style.textContent = `
        @media screen and (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
                position: fixed;
                top: 0;
                left: 0;
                height: 100vh;
                z-index: 1000;
                transition: transform 0.3s ease;
                width: 250px;
                box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            }
            
            .sidebar.open {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0;
                width: 100%;
            }
            
            .sidebar-toggle {
                display: block;
                position: fixed;
                top: 15px;
                left: 15px;
                z-index: 1001;
                background: #fff;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                cursor: pointer;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            
            body {
                padding-top: 60px;
            }
        }
        
        @media screen and (min-width: 769px) {
            .sidebar-toggle {
                display: none;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Toggle sidebar on button click
    toggleButton.addEventListener('click', function() {
        sidebar.classList.toggle('open');
    });
    
    // Close sidebar when clicking outside of it (on mobile)
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768 && 
            !sidebar.contains(event.target) && 
            !toggleButton.contains(event.target) && 
            sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('open');
        }
    });
    
    // Close sidebar when a link is clicked (mobile)
    const sidebarLinks = sidebar.querySelectorAll('a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('open');
            }
        });
    });
});