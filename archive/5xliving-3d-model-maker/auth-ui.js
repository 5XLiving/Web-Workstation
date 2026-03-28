/**
 * Authentication UI for 5XLiving 3D Maker
 */

import apiClient from './api-client.js';

export class AuthUI {
    constructor(container) {
        this.container = container;
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
        this.checkLoginStatus();
    }

    render() {
        this.container.innerHTML = `
            <div id="auth-panel" class="auth-panel">
                <div id="logged-out-view" class="auth-view" style="display: none;">
                    <button id="show-login-btn" class="btn btn-primary">Login</button>
                    <button id="show-register-btn" class="btn btn-secondary">Sign Up</button>
                </div>

                <div id="logged-in-view" class="auth-view" style="display: none;">
                    <span id="user-email" class="user-email"></span>
                    <span id="user-membership" class="membership-badge"></span>
                    <span id="user-quota" class="quota-display"></span>
                    <button id="logout-btn" class="btn btn-small">Logout</button>
                </div>

                <!-- Login Modal -->
                <div id="login-modal" class="modal" style="display: none;">
                    <div class="modal-content">
                        <h2>Login</h2>
                        <form id="login-form">
                            <input type="email" id="login-email" placeholder="Email" required>
                            <input type="password" id="login-password" placeholder="Password" required>
                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary">Login</button>
                                <button type="button" id="cancel-login-btn" class="btn btn-secondary">Cancel</button>
                            </div>
                        </form>
                        <p class="error-message" id="login-error"></p>
                    </div>
                </div>

                <!-- Register Modal -->
                <div id="register-modal" class="modal" style="display: none;">
                    <div class="modal-content">
                        <h2>Sign Up</h2>
                        <form id="register-form">
                            <input type="email" id="register-email" placeholder="Email" required>
                            <input type="password" id="register-password" placeholder="Password (min 6 chars)" required>
                            <select id="register-membership">
                                <option value="free">Free (1 generation/day)</option>
                                <option value="paid">Paid ($9.99/mo - 100/day)</option>
                            </select>
                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary">Sign Up</button>
                                <button type="button" id="cancel-register-btn" class="btn btn-secondary">Cancel</button>
                            </div>
                        </form>
                        <p class="error-message" id="register-error"></p>
                    </div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Show login modal
        document.getElementById('show-login-btn')?.addEventListener('click', () => {
            this.showModal('login-modal');
        });

        // Show register modal
        document.getElementById('show-register-btn')?.addEventListener('click', () => {
            this.showModal('register-modal');
        });

        // Cancel buttons
        document.getElementById('cancel-login-btn')?.addEventListener('click', () => {
            this.hideModal('login-modal');
        });
        document.getElementById('cancel-register-btn')?.addEventListener('click', () => {
            this.hideModal('register-modal');
        });

        // Login form
        document.getElementById('login-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin();
        });

        // Register form
        document.getElementById('register-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleRegister();
        });

        // Logout button
        document.getElementById('logout-btn')?.addEventListener('click', () => {
            this.handleLogout();
        });
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
        // Clear error messages
        document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    }

    async handleLogin() {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const errorEl = document.getElementById('login-error');

        try {
            errorEl.textContent = 'Logging in...';
            const response = await apiClient.login(email, password);
            
            this.hideModal('login-modal');
            this.updateUI();
            
            // Show success message
            if (window.addLog) {
                window.addLog(`Welcome back, ${email}!`, 'success');
            }
            
        } catch (error) {
            errorEl.textContent = error.message;
            errorEl.style.color = 'red';
        }
    }

    async handleRegister() {
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const membership = document.getElementById('register-membership').value;
        const errorEl = document.getElementById('register-error');

        try {
            errorEl.textContent = 'Creating account...';
            const response = await apiClient.register(email, password, membership);
            
            this.hideModal('register-modal');
            this.updateUI();
            
            // Show success message
            if (window.addLog) {
                window.addLog(`Account created! Welcome, ${email}!`, 'success');
            }
            
        } catch (error) {
            errorEl.textContent = error.message;
            errorEl.style.color = 'red';
        }
    }

    handleLogout() {
        apiClient.logout();
        this.updateUI();
        
        if (window.addLog) {
            window.addLog('Logged out successfully', 'info');
        }
    }

    async checkLoginStatus() {
        if (apiClient.isLoggedIn()) {
            await apiClient.getStatus();
        }
        this.updateUI();
    }

    async updateUI() {
        const loggedOutView = document.getElementById('logged-out-view');
        const loggedInView = document.getElementById('logged-in-view');
        const userEmailEl = document.getElementById('user-email');
        const membershipEl = document.getElementById('user-membership');
        const quotaEl = document.getElementById('user-quota');

        if (apiClient.isLoggedIn()) {
            // Show logged-in view
            loggedOutView.style.display = 'none';
            loggedInView.style.display = 'flex';

            // Update user info
            userEmailEl.textContent = apiClient.user.email;
            
            // Update membership badge
            const isPaid = apiClient.isPaid();
            membershipEl.textContent = isPaid ? 'VIP' : 'Free';
            membershipEl.className = `membership-badge ${isPaid ? 'paid' : 'free'}`;

            // Update quota
            const quotaData = await apiClient.getQuota();
            if (quotaData) {
                quotaEl.textContent = `${quotaData.remaining}/${quotaData.quota.daily_generations} today`;
            }
        } else {
            // Show logged-out view
            loggedOutView.style.display = 'flex';
            loggedInView.style.display = 'none';
        }
    }

    async refreshQuota() {
        if (apiClient.isLoggedIn()) {
            const quotaData = await apiClient.getQuota();
            if (quotaData) {
                const quotaEl = document.getElementById('user-quota');
                if (quotaEl) {
                    quotaEl.textContent = `${quotaData.remaining}/${quotaData.quota.daily_generations} today`;
                }
            }
        }
    }
}

export default AuthUI;
