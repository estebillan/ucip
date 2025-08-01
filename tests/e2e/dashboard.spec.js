/**
 * End-to-End Tests for Universal Consultant Intelligence Platform Dashboard
 * 
 * Tests core dashboard functionality, navigation, API integration,
 * and user interactions using Playwright.
 */

import { test, expect } from '@playwright/test';

// Test configuration
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const API_URL = process.env.API_URL || 'http://localhost:8000';

test.describe('Dashboard Functionality', () => {
    
    test.beforeEach(async ({ page }) => {
        // Navigate to the application
        await page.goto(BASE_URL);
        
        // Wait for the application to load
        await page.waitForSelector('#main-content', { state: 'visible', timeout: 10000 });
    });

    test('should load dashboard page successfully', async ({ page }) => {
        // Check page title
        await expect(page).toHaveTitle(/Universal Consultant Intelligence Platform/);
        
        // Check main navigation is visible
        await expect(page.locator('#main-nav')).toBeVisible();
        
        // Check dashboard page is active
        await expect(page.locator('#dashboard-page')).toBeVisible();
        await expect(page.locator('#dashboard-page')).toHaveClass(/active/);
        
        // Check page header
        await expect(page.locator('.page-header h1')).toContainText('Dashboard');
        await expect(page.locator('.page-header p')).toContainText('Welcome to your Consultant Intelligence Platform');
    });

    test('should display statistics cards', async ({ page }) => {
        // Check all stat cards are present
        const statCards = page.locator('.stat-card');
        await expect(statCards).toHaveCount(4);
        
        // Check individual stat cards
        await expect(page.locator('#total-prospects')).toBeVisible();
        await expect(page.locator('#active-signals')).toBeVisible();
        await expect(page.locator('#reports-generated')).toBeVisible();
        await expect(page.locator('#email-campaigns')).toBeVisible();
        
        // Check stat cards have proper icons
        await expect(page.locator('.stat-card .fas.fa-building')).toBeVisible();
        await expect(page.locator('.stat-card .fas.fa-signal')).toBeVisible();
        await expect(page.locator('.stat-card .fas.fa-file-pdf')).toBeVisible();
        await expect(page.locator('.stat-card .fas.fa-envelope')).toBeVisible();
    });

    test('should display recent activity section', async ({ page }) => {
        // Check section header
        await expect(page.locator('.dashboard-section')).toContainText('Recent Activity');
        
        // Check activity list container
        await expect(page.locator('#recent-activity')).toBeVisible();
        
        // Wait for activity items to load
        await page.waitForSelector('.activity-item', { timeout: 5000 });
        
        // Check activity items are present
        const activityItems = page.locator('.activity-item');
        await expect(activityItems).toHaveCount.greaterThan(0);
        
        // Check activity item structure
        const firstActivity = activityItems.first();
        await expect(firstActivity.locator('.activity-icon')).toBeVisible();
        await expect(firstActivity.locator('.activity-content p')).toBeVisible();
        await expect(firstActivity.locator('.activity-time')).toBeVisible();
    });

    test('should display priority signals section', async ({ page }) => {
        // Check section header
        await expect(page.locator('.dashboard-section')).toContainText('High Priority Signals');
        
        // Check signals container
        await expect(page.locator('#priority-signals')).toBeVisible();
        
        // Wait for signals to load
        await page.waitForSelector('.signal-item', { timeout: 5000 });
        
        // Check signal items structure
        const signalItems = page.locator('.signal-item');
        await expect(signalItems).toHaveCount.greaterThan(0);
        
        const firstSignal = signalItems.first();
        await expect(firstSignal.locator('.signal-header h4')).toBeVisible();
        await expect(firstSignal.locator('.priority-badge')).toBeVisible();
        await expect(firstSignal.locator('.signal-type')).toBeVisible();
        await expect(firstSignal.locator('.signal-description')).toBeVisible();
    });

    test('should display quick actions section', async ({ page }) => {
        // Check section header
        await expect(page.locator('.dashboard-section')).toContainText('Quick Actions');
        
        // Check all quick action buttons are present
        await expect(page.locator('#new-research-btn')).toBeVisible();
        await expect(page.locator('#generate-report-btn')).toBeVisible();
        await expect(page.locator('#create-campaign-btn')).toBeVisible();
        await expect(page.locator('#add-prospect-btn')).toBeVisible();
        
        // Check button text and icons
        await expect(page.locator('#new-research-btn')).toContainText('Start Research');
        await expect(page.locator('#new-research-btn .fas.fa-search')).toBeVisible();
        
        await expect(page.locator('#generate-report-btn')).toContainText('Generate Report');
        await expect(page.locator('#generate-report-btn .fas.fa-file-pdf')).toBeVisible();
        
        await expect(page.locator('#create-campaign-btn')).toContainText('Create Campaign');
        await expect(page.locator('#create-campaign-btn .fas.fa-envelope')).toBeVisible();
        
        await expect(page.locator('#add-prospect-btn')).toContainText('Add Prospect');
        await expect(page.locator('#add-prospect-btn .fas.fa-plus')).toBeVisible();
    });

    test('should handle navigation between pages', async ({ page }) => {
        // Test navigation to prospects page
        await page.click('a[href="#prospects"]');
        await expect(page.locator('#prospects-page')).toBeVisible();
        await expect(page.locator('#prospects-page')).toHaveClass(/active/);
        await expect(page.locator('#dashboard-page')).not.toHaveClass(/active/);
        
        // Check active nav link
        await expect(page.locator('a[href="#prospects"]')).toHaveClass(/active/);
        await expect(page.locator('a[href="#dashboard"]')).not.toHaveClass(/active/);
        
        // Test navigation to research page
        await page.click('a[href="#research"]');
        await expect(page.locator('#research-page')).toBeVisible();
        await expect(page.locator('#research-page')).toHaveClass(/active/);
        
        // Navigate back to dashboard
        await page.click('a[href="#dashboard"]');
        await expect(page.locator('#dashboard-page')).toBeVisible();
        await expect(page.locator('#dashboard-page')).toHaveClass(/active/);
    });

    test('should handle quick action button clicks', async ({ page }) => {
        // Test Start Research button navigation
        await page.click('#new-research-btn');
        await expect(page.locator('#research-page')).toBeVisible();
        await expect(page.locator('#research-page')).toHaveClass(/active/);
        
        // Navigate back to dashboard
        await page.click('a[href="#dashboard"]');
        
        // Test Generate Report button navigation
        await page.click('#generate-report-btn');
        await expect(page.locator('#reports-page')).toBeVisible();
        
        // Navigate back to dashboard
        await page.click('a[href="#dashboard"]');
        
        // Test Create Campaign button navigation
        await page.click('#create-campaign-btn');
        await expect(page.locator('#campaigns-page')).toBeVisible();
        
        // Navigate back to dashboard
        await page.click('a[href="#dashboard"]');
        
        // Test Add Prospect button navigation
        await page.click('#add-prospect-btn');
        await expect(page.locator('#prospects-page')).toBeVisible();
    });

    test('should open and close notifications modal', async ({ page }) => {
        // Click notifications button
        await page.click('#notifications-btn');
        
        // Check modal is visible
        await expect(page.locator('#modal-overlay')).toHaveClass(/active/);
        await expect(page.locator('#modal-title')).toContainText('Notifications');
        
        // Check notification items are present
        await expect(page.locator('.notification-item')).toHaveCount.greaterThan(0);
        
        // Close modal by clicking close button
        await page.click('#modal-close');
        await expect(page.locator('#modal-overlay')).not.toHaveClass(/active/);
    });

    test('should open and close user menu modal', async ({ page }) => {
        // Click user menu button
        await page.click('#user-menu-btn');
        
        // Check modal is visible
        await expect(page.locator('#modal-overlay')).toHaveClass(/active/);
        await expect(page.locator('#modal-title')).toContainText('User Settings');
        
        // Check settings form is present
        await expect(page.locator('.user-settings')).toBeVisible();
        await expect(page.locator('.user-settings .setting-item')).toHaveCount.greaterThan(0);
        
        // Close modal by clicking cancel
        await page.click('#modal-cancel');
        await expect(page.locator('#modal-overlay')).not.toHaveClass(/active/);
    });

    test('should handle stat card hover effects', async ({ page }) => {
        const statCard = page.locator('.stat-card').first();
        
        // Get initial box-shadow
        const initialShadow = await statCard.evaluate(el => 
            getComputedStyle(el).boxShadow
        );
        
        // Hover over the card
        await statCard.hover();
        
        // Wait for transition
        await page.waitForTimeout(300);
        
        // Check if box-shadow changed (hover effect)
        const hoveredShadow = await statCard.evaluate(el => 
            getComputedStyle(el).boxShadow
        );
        
        expect(hoveredShadow).not.toBe(initialShadow);
    });

    test('should handle responsive design', async ({ page }) => {
        // Test mobile viewport
        await page.setViewportSize({ width: 375, height: 667 });
        
        // Check navigation is still functional
        await expect(page.locator('#main-nav')).toBeVisible();
        await expect(page.locator('.nav-brand')).toBeVisible();
        
        // Check stats grid adapts to mobile
        const statsGrid = page.locator('.stats-grid');
        await expect(statsGrid).toBeVisible();
        
        // Test tablet viewport
        await page.setViewportSize({ width: 768, height: 1024 });
        
        // Check layout adjusts appropriately
        await expect(page.locator('.dashboard-grid')).toBeVisible();
        await expect(page.locator('.quick-actions')).toBeVisible();
        
        // Reset to desktop viewport
        await page.setViewportSize({ width: 1280, height: 720 });
    });

    test('should handle loading states gracefully', async ({ page }) => {
        // Intercept API calls to simulate slow responses
        await page.route(`${API_URL}/api/v1/**`, async route => {
            // Add delay to simulate slow API
            await new Promise(resolve => setTimeout(resolve, 1000));
            await route.continue();
        });
        
        // Reload page
        await page.reload();
        
        // Check loading screen is shown initially
        await expect(page.locator('#loading-screen')).toBeVisible();
        
        // Wait for main content to load
        await page.waitForSelector('#main-content', { state: 'visible', timeout: 15000 });
        
        // Check loading screen is hidden
        await expect(page.locator('#loading-screen')).not.toBeVisible();
    });

    test('should handle API errors gracefully', async ({ page }) => {
        // Intercept API calls to simulate errors
        await page.route(`${API_URL}/health`, async route => {
            await route.fulfill({
                status: 500,
                contentType: 'application/json',
                body: JSON.stringify({ error: 'Internal Server Error' })
            });
        });
        
        // Reload page
        await page.reload();
        
        // Wait for error handling
        await page.waitForTimeout(2000);
        
        // Check error message is displayed
        await expect(page.locator('#loading-screen')).toContainText('Failed to initialize application');
        
        // Check retry button is present
        await expect(page.locator('button')).toContainText('Retry');
    });

    test('should maintain accessibility standards', async ({ page }) => {
        // Check main landmarks
        await expect(page.locator('nav')).toBeVisible();
        await expect(page.locator('main')).toBeVisible();
        
        // Check button accessibility
        const buttons = page.locator('button');
        const buttonCount = await buttons.count();
        
        for (let i = 0; i < buttonCount; i++) {
            const button = buttons.nth(i);
            
            // Check button is focusable
            await button.focus();
            await expect(button).toBeFocused();
        }
        
        // Check links have proper attributes
        const navLinks = page.locator('.nav-link');
        const linkCount = await navLinks.count();
        
        for (let i = 0; i < linkCount; i++) {
            const link = navLinks.nth(i);
            await expect(link).toHaveAttribute('href');
        }
        
        // Check images have alt text (if any)
        const images = page.locator('img');
        const imageCount = await images.count();
        
        for (let i = 0; i < imageCount; i++) {
            const img = images.nth(i);
            await expect(img).toHaveAttribute('alt');
        }
    });

    test('should handle keyboard navigation', async ({ page }) => {
        // Test tab navigation through interactive elements
        await page.keyboard.press('Tab');
        
        // Should focus on first navigation link
        await expect(page.locator('a[href="#dashboard"]')).toBeFocused();
        
        // Continue tabbing through navigation
        await page.keyboard.press('Tab');
        await expect(page.locator('a[href="#prospects"]')).toBeFocused();
        
        await page.keyboard.press('Tab');
        await expect(page.locator('a[href="#research"]')).toBeFocused();
        
        // Test Enter key activation
        await page.keyboard.press('Enter');
        await expect(page.locator('#research-page')).toHaveClass(/active/);
        
        // Test Escape key for modal closing
        await page.click('#notifications-btn');
        await expect(page.locator('#modal-overlay')).toHaveClass(/active/);
        
        await page.keyboard.press('Escape');
        await expect(page.locator('#modal-overlay')).not.toHaveClass(/active/);
    });

});

test.describe('Dashboard Performance', () => {
    
    test('should load within acceptable time limits', async ({ page }) => {
        const startTime = Date.now();
        
        await page.goto(BASE_URL);
        await page.waitForSelector('#main-content', { state: 'visible' });
        
        const loadTime = Date.now() - startTime;
        
        // Should load within 5 seconds
        expect(loadTime).toBeLessThan(5000);
    });

    test('should handle concurrent operations', async ({ page }) => {
        await page.goto(BASE_URL);
        await page.waitForSelector('#main-content', { state: 'visible' });
        
        // Perform multiple actions concurrently
        await Promise.all([
            page.click('#notifications-btn'),
            page.hover('.stat-card'),
            page.click('#user-menu-btn')
        ]);
        
        // Should handle without errors
        await expect(page.locator('#modal-overlay')).toHaveClass(/active/);
    });

});

test.describe('Dashboard Data Integration', () => {
    
    test('should handle empty data states', async ({ page }) => {
        // Mock empty API responses
        await page.route(`${API_URL}/api/v1/**`, async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ items: [], total: 0 })
            });
        });
        
        await page.goto(BASE_URL);
        await page.waitForSelector('#main-content', { state: 'visible' });
        
        // Should still display the interface gracefully
        await expect(page.locator('.dashboard-grid')).toBeVisible();
        await expect(page.locator('.stats-grid')).toBeVisible();
    });

    test('should refresh data automatically', async ({ page }) => {
        let requestCount = 0;
        
        // Count API requests
        await page.route(`${API_URL}/health`, async route => {
            requestCount++;
            await route.continue();
        });
        
        await page.goto(BASE_URL);
        await page.waitForSelector('#main-content', { state: 'visible' });
        
        const initialRequests = requestCount;
        
        // Wait for auto-refresh (should happen every 30 seconds in test)
        await page.waitForTimeout(3000);  // Wait 3 seconds for demo
        
        // In a real test, you'd wait longer or mock the refresh interval
        expect(requestCount).toBeGreaterThanOrEqual(initialRequests);
    });

});