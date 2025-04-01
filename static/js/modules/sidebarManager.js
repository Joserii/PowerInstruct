// modules/sidebarManager.js
export class SidebarManager {
    constructor(config) {
        this.sidebar = config.sidebar;
        this.sidebarToggle = config.sidebarToggle;
        this.sidebarIcon = document.getElementById('sidebarIcon');
        this.isOpen = false; // Add status tracking
        this.init();
    }

    async init() {
        try {
            const response = await fetch('/static/html/sidebar.html');
            const html = await response.text();
            this.sidebar.innerHTML = html;
            
            this.createOverlay();
            this.initializeEventListeners();
        } catch (error) {
            console.error('Error loading sidebar:', error);
        }
    }

    createOverlay() {
        if (!document.querySelector('.sidebar-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
        }
    }

    initializeEventListeners() {
        // Open the sidebar
        this.sidebarToggle.addEventListener('click', () => {
            this.toggleSidebar();
        });

        // Close button event
        const closeBtn = this.sidebar.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.closeSidebar();
            });
        }

        const overlay = document.querySelector('.sidebar-overlay');
        if (overlay) {
            overlay.addEventListener('click', () => {
                this.closeSidebar();
            });
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeSidebar();
            }
        });
    }

    toggleSidebar() {
        if (this.isOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    openSidebar() {
        this.sidebar.classList.add('active');
        document.querySelector('.sidebar-overlay').classList.add('active');
        this.sidebarIcon.classList.remove('bi-question-circle');
        this.sidebarIcon.classList.add('bi-x-circle'); 
        this.isOpen = true;
        this.sidebarToggle.title = "Close User Guide";
    }

    closeSidebar() {
        this.sidebar.classList.remove('active');
        document.querySelector('.sidebar-overlay').classList.remove('active');
        this.sidebarIcon.classList.remove('bi-x-circle');
        this.sidebarIcon.classList.add('bi-question-circle'); 
        this.isOpen = false;
        this.sidebarToggle.title = "Usage Process Guide";
    }
}
