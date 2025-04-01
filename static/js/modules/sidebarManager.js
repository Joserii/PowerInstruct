// modules/sidebarManager.js
export class SidebarManager {
    constructor(config) {
        this.sidebar = config.sidebar;
        this.sidebarToggle = config.sidebarToggle;
        this.sidebarIcon = document.getElementById('sidebarIcon');
        this.isOpen = false; // 添加状态跟踪
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
        // 打开侧边栏
        this.sidebarToggle.addEventListener('click', () => {
            this.toggleSidebar();
        });

        // 关闭按钮事件
        const closeBtn = this.sidebar.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.closeSidebar();
            });
        }

        // 遮罩层点击事件
        const overlay = document.querySelector('.sidebar-overlay');
        if (overlay) {
            overlay.addEventListener('click', () => {
                this.closeSidebar();
            });
        }

        // ESC键关闭
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
        this.sidebarIcon.classList.add('bi-x-circle'); // 改变图标为关闭图标
        this.isOpen = true;
        this.sidebarToggle.title = "关闭使用指南";
    }

    closeSidebar() {
        this.sidebar.classList.remove('active');
        document.querySelector('.sidebar-overlay').classList.remove('active');
        this.sidebarIcon.classList.remove('bi-x-circle');
        this.sidebarIcon.classList.add('bi-question-circle'); // 恢复原始图标
        this.isOpen = false;
        this.sidebarToggle.title = "使用流程指南";
    }
}
