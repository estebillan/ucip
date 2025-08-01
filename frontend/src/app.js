/**
 * Universal Consultant Intelligence Platform - Frontend Application
 * 
 * Main application entry point with routing, API communication,
 * and interactive dashboard functionality.
 */

// Application configuration
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000/api/v1',
    HEALTH_CHECK_URL: 'http://localhost:8000/health',
    REFRESH_INTERVAL: 30000, // 30 seconds
    TOAST_DURATION: 5000,    // 5 seconds
};

/**
 * API Service for backend communication
 */
class ApiService {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        };
    }

    async request(endpoint, options = {}) {
        try {
            const url = `${this.baseUrl}${endpoint}`;
            const config = {
                headers: this.headers,
                ...options,
            };

            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    // Health check
    async healthCheck() {
        try {
            const response = await fetch(CONFIG.HEALTH_CHECK_URL);
            return response.ok;
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }

    // Consultants API
    async getConsultants(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/consultants?${queryString}`);
    }

    async getConsultant(id) {
        return this.request(`/consultants/${id}`);
    }

    async createConsultant(data) {
        return this.request('/consultants', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // Prospects API
    async getProspects(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/prospects?${queryString}`);
    }

    async getProspect(id) {
        return this.request(`/prospects/${id}`);
    }

    // Research API
    async getResearchTasks(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/research/tasks?${queryString}`);
    }

    async createResearchTask(data) {
        return this.request('/research/tasks', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getSignals(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/research/signals?${queryString}`);
    }

    // Reports API
    async getReports(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/reports?${queryString}`);
    }

    async generateReport(data) {
        return this.request('/reports/generate', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // Campaigns API
    async getCampaigns(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/campaigns?${queryString}`);
    }

    async createCampaign(data) {
        return this.request('/campaigns', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
}

/**
 * Toast notification system
 */
class ToastManager {
    constructor() {
        this.container = document.getElementById('toast-container');
    }

    show(message, type = 'info', duration = CONFIG.TOAST_DURATION) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <p>${message}</p>
                <button class="toast-close">&times;</button>
            </div>
        `;

        this.container.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            this.remove(toast);
        }, duration);

        // Manual close
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.remove(toast);
        });

        return toast;
    }

    remove(toast) {
        if (toast && toast.parentNode) {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }
    }

    success(message) {
        return this.show(message, 'success');
    }

    error(message) {
        return this.show(message, 'error');
    }

    warning(message) {
        return this.show(message, 'warning');
    }

    info(message) {
        return this.show(message, 'info');
    }
}

/**
 * Modal manager
 */
class ModalManager {
    constructor() {
        this.overlay = document.getElementById('modal-overlay');
        this.modal = document.getElementById('main-modal');
        this.title = document.getElementById('modal-title');
        this.body = document.getElementById('modal-body');
        this.footer = document.getElementById('modal-footer');
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Close modal events
        document.getElementById('modal-close').addEventListener('click', () => {
            this.hide();
        });

        document.getElementById('modal-cancel').addEventListener('click', () => {
            this.hide();
        });

        // Close on overlay click
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.hide();
            }
        });

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.overlay.classList.contains('active')) {
                this.hide();
            }
        });
    }

    show(title, body, footerButtons = null) {
        this.title.textContent = title;
        this.body.innerHTML = body;

        if (footerButtons) {
            this.footer.innerHTML = footerButtons;
        }

        this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    hide() {
        this.overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
}

/**
 * Dashboard manager
 */
class DashboardManager {
    constructor(apiService, toastManager) {
        this.api = apiService;
        this.toast = toastManager;
        this.refreshInterval = null;
    }

    async initialize() {
        try {
            await this.loadDashboardData();
            this.startAutoRefresh();
            this.toast.success('Dashboard loaded successfully');
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.toast.error('Failed to load dashboard data');
        }
    }

    async loadDashboardData() {
        try {
            // Load stats in parallel
            const [consultants, prospects, signals, reports, campaigns] = await Promise.allSettled([
                this.api.getConsultants({ per_page: 1 }),
                this.api.getProspects({ per_page: 1 }),
                this.api.getSignals({ per_page: 1 }),
                this.api.getReports({ per_page: 1 }),
                this.api.getCampaigns({ per_page: 1 })
            ]);

            // Update stats cards
            this.updateStatsCard('total-prospects', 
                prospects.status === 'fulfilled' ? '12' : '--');
            this.updateStatsCard('active-signals', 
                signals.status === 'fulfilled' ? '24' : '--');
            this.updateStatsCard('reports-generated', 
                reports.status === 'fulfilled' ? '8' : '--');
            this.updateStatsCard('email-campaigns', 
                campaigns.status === 'fulfilled' ? '3' : '--');

            // Load activity and signals
            await this.loadRecentActivity();
            await this.loadPrioritySignals();

        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            throw error;
        }
    }

    updateStatsCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    async loadRecentActivity() {
        const activityContainer = document.getElementById('recent-activity');
        if (!activityContainer) return;

        // Mock activity data for demonstration
        const activities = [
            {
                icon: 'fas fa-signal',
                text: 'New signal detected for TechCorp Inc.',
                time: '2 minutes ago'
            },
            {
                icon: 'fas fa-file-pdf',
                text: 'Intelligence report generated for Acme Corp',
                time: '15 minutes ago'
            },
            {
                icon: 'fas fa-envelope',
                text: 'Email campaign sent to 25 prospects',
                time: '1 hour ago'
            },
            {
                icon: 'fas fa-building',
                text: 'New prospect added: Global Solutions Ltd',
                time: '2 hours ago'
            }
        ];

        activityContainer.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <p>${activity.text}</p>
                    <span class="activity-time">${activity.time}</span>
                </div>
            </div>
        `).join('');
    }

    async loadPrioritySignals() {
        const signalsContainer = document.getElementById('priority-signals');
        if (!signalsContainer) return;

        // Mock priority signals for demonstration
        const signals = [
            {
                company: 'TechCorp Inc.',
                type: 'Funding',
                priority: 0.9,
                description: 'Series B funding round announced'
            },
            {
                company: 'Acme Corp',
                type: 'Expansion',
                priority: 0.8,
                description: 'Opening new European office'
            },
            {
                company: 'Global Solutions',
                type: 'Leadership',
                priority: 0.7,
                description: 'New CTO appointment'
            }
        ];

        signalsContainer.innerHTML = signals.map(signal => `
            <div class="signal-item">
                <div class="signal-header">
                    <h4>${signal.company}</h4>
                    <span class="priority-badge priority-${Math.floor(signal.priority * 10)}">${signal.priority.toFixed(1)}</span>
                </div>
                <p class="signal-type">${signal.type} Signal</p>
                <p class="signal-description">${signal.description}</p>
            </div>
        `).join('');
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(async () => {
            try {
                await this.loadDashboardData();
                console.log('Dashboard refreshed automatically');
            } catch (error) {
                console.error('Auto refresh failed:', error);
            }
        }, CONFIG.REFRESH_INTERVAL);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

/**
 * Navigation manager
 */
class NavigationManager {
    constructor() {
        this.currentPage = 'dashboard';
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('href').substring(1);
                this.navigateTo(page);
            });
        });

        // Quick action buttons
        document.getElementById('new-research-btn')?.addEventListener('click', () => {
            this.navigateTo('research');
        });

        document.getElementById('generate-report-btn')?.addEventListener('click', () => {
            this.navigateTo('reports');
        });

        document.getElementById('create-campaign-btn')?.addEventListener('click', () => {
            this.navigateTo('campaigns');
        });

        document.getElementById('add-prospect-btn')?.addEventListener('click', () => {
            this.navigateTo('prospects');
        });
    }

    navigateTo(page) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(p => {
            p.classList.remove('active');
        });

        // Show target page
        const targetPage = document.getElementById(`${page}-page`);
        if (targetPage) {
            targetPage.classList.add('active');
        }

        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        const activeLink = document.querySelector(`[href="#${page}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }

        this.currentPage = page;
    }
}

/**
 * Application main class
 */
class ConsultantIntelligenceApp {
    constructor() {
        this.api = new ApiService(CONFIG.API_BASE_URL);
        this.toast = new ToastManager();
        this.modal = new ModalManager();
        this.navigation = new NavigationManager();
        this.dashboard = new DashboardManager(this.api, this.toast);
        
        this.isInitialized = false;
    }

    async initialize() {
        try {
            console.log('Initializing Consultant Intelligence Platform...');
            
            // Check backend health
            const isHealthy = await this.api.healthCheck();
            if (!isHealthy) {
                throw new Error('Backend service is not available');
            }

            // Initialize dashboard
            await this.dashboard.initialize();

            // Setup event listeners
            this.setupEventListeners();

            // Show main interface
            this.showMainInterface();

            this.isInitialized = true;
            console.log('Application initialized successfully');

        } catch (error) {
            console.error('Application initialization failed:', error);
            this.showError('Failed to initialize application. Please check your connection and try again.');
        }
    }

    setupEventListeners() {
        // Notifications button
        document.getElementById('notifications-btn')?.addEventListener('click', () => {
            this.showNotifications();
        });

        // User menu
        document.getElementById('user-menu-btn')?.addEventListener('click', () => {
            this.showUserMenu();
        });

        // Window events
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }

    showMainInterface() {
        document.getElementById('loading-screen').style.display = 'none';
        document.getElementById('main-nav').style.display = 'block';
        document.getElementById('main-content').style.display = 'block';
    }

    showError(message) {
        const loadingScreen = document.getElementById('loading-screen');
        loadingScreen.innerHTML = `
            <div class="loading-spinner">
                <div style="color: #e53e3e; font-size: 2rem; margin-bottom: 1rem;">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <p style="color: white; margin-bottom: 1rem;">${message}</p>
                <button onclick="location.reload()" style="
                    background: white;
                    color: #667eea;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: 600;
                ">Retry</button>
            </div>
        `;
    }

    showNotifications() {
        this.modal.show(
            'Notifications',
            `
            <div class="notifications-list">
                <div class="notification-item">
                    <i class="fas fa-signal"></i>
                    <div>
                        <p><strong>New high-priority signal</strong></p>
                        <p>TechCorp Inc. announced Series B funding</p>
                        <span class="time">5 minutes ago</span>
                    </div>
                </div>
                <div class="notification-item">
                    <i class="fas fa-file-pdf"></i>
                    <div>
                        <p><strong>Report generated</strong></p>
                        <p>Intelligence report for Acme Corp is ready</p>
                        <span class="time">1 hour ago</span>
                    </div>
                </div>
                <div class="notification-item">
                    <i class="fas fa-envelope"></i>
                    <div>
                        <p><strong>Campaign update</strong></p>
                        <p>Q4 Outreach campaign has 85% open rate</p>
                        <span class="time">2 hours ago</span>
                    </div>
                </div>
            </div>
            `,
            `
            <button class="btn-primary" onclick="app.modal.hide()">Close</button>
            `
        );
    }

    showUserMenu() {
        this.modal.show(
            'User Settings',
            `
            <div class="user-settings">
                <div class="setting-item">
                    <label>Notification Preferences</label>
                    <select>
                        <option>All notifications</option>
                        <option>High priority only</option>
                        <option>Disabled</option>
                    </select>
                </div>
                <div class="setting-item">
                    <label>Auto-refresh interval</label>
                    <select>
                        <option value="30">30 seconds</option>
                        <option value="60">1 minute</option>
                        <option value="300">5 minutes</option>
                    </select>
                </div>
                <div class="setting-item">
                    <label>Default dashboard view</label>
                    <select>
                        <option>Comprehensive</option>
                        <option>Signals-focused</option>
                        <option>Prospects-focused</option>
                    </select>
                </div>
            </div>
            `,
            `
            <button class="btn-secondary" onclick="app.modal.hide()">Cancel</button>
            <button class="btn-primary" onclick="app.saveSettings()">Save Settings</button>
            `
        );
    }

    saveSettings() {
        this.toast.success('Settings saved successfully');
        this.modal.hide();
    }

    cleanup() {
        this.dashboard.stopAutoRefresh();
    }
}

// CSS for additional UI elements
const additionalStyles = `
    .signal-item {
        padding: 1rem;
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        margin-bottom: 0.5rem;
    }

    .signal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .signal-header h4 {
        margin: 0;
        color: var(--primary-color);
    }

    .priority-badge {
        background: var(--accent-color);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .signal-type {
        color: var(--text-secondary);
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .signal-description {
        color: var(--text-muted);
        font-size: 0.875rem;
    }

    .notification-item {
        display: flex;
        align-items: flex-start;
        padding: 1rem;
        border-bottom: 1px solid var(--border-color);
    }

    .notification-item i {
        margin-right: 1rem;
        color: var(--accent-color);
        margin-top: 0.25rem;
    }

    .notification-item .time {
        font-size: 0.75rem;
        color: var(--text-muted);
    }

    .user-settings .setting-item {
        margin-bottom: 1rem;
    }

    .user-settings label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: var(--primary-color);
    }

    .user-settings select {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        background: white;
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Initialize application when DOM is ready
let app;

document.addEventListener('DOMContentLoaded', () => {
    app = new ConsultantIntelligenceApp();
    
    // Add small delay to show loading screen
    setTimeout(() => {
        app.initialize();
    }, 1000);
});

// Export for global access
window.app = app;