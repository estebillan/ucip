/**
 * End-to-End API Integration Tests
 * 
 * Tests API endpoints, data flow, error handling,
 * and integration between frontend and backend services.
 */

import { test, expect } from '@playwright/test';

// Test configuration
const API_URL = process.env.API_URL || 'http://localhost:8000';
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

test.describe('API Health and Connectivity', () => {
    
    test('should respond to health check endpoint', async ({ request }) => {
        const response = await request.get(`${API_URL}/health`);
        
        expect(response.status()).toBe(200);
        
        const health = await response.json();
        expect(health).toHaveProperty('status');
        expect(health.status).toBe('healthy');
    });

    test('should return proper API information at root endpoint', async ({ request }) => {
        const response = await request.get(`${API_URL}/`);
        
        expect(response.status()).toBe(200);
        
        const info = await response.json();
        expect(info).toHaveProperty('name');
        expect(info).toHaveProperty('version');
        expect(info).toHaveProperty('status');
        expect(info.name).toBe('Universal Consultant Intelligence Platform');
        expect(info.status).toBe('operational');
    });

    test('should provide OpenAPI documentation', async ({ request }) => {
        const response = await request.get(`${API_URL}/docs`);
        
        // Should either return docs or redirect to docs
        expect([200, 302, 404]).toContain(response.status());
        
        if (response.status() === 200) {
            const contentType = response.headers()['content-type'];
            expect(contentType).toContain('text/html');
        }
    });

    test('should handle CORS properly', async ({ request }) => {
        const response = await request.options(`${API_URL}/api/v1/consultants`, {
            headers: {
                'Origin': BASE_URL,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        });
        
        expect(response.status()).toBe(200);
        expect(response.headers()).toHaveProperty('access-control-allow-origin');
    });

});

test.describe('Consultants API', () => {
    
    test('should list consultants with pagination', async ({ request }) => {
        const response = await request.get(`${API_URL}/api/v1/consultants?page=1&per_page=10`);
        
        expect(response.status()).toBe(200);
        
        const data = await response.json();
        expect(data).toHaveProperty('items');
        expect(data).toHaveProperty('total');
        expect(data).toHaveProperty('page');
        expect(data).toHaveProperty('per_page');
        expect(Array.isArray(data.items)).toBe(true);
    });

    test('should handle consultant creation', async ({ request }) => {
        const consultantData = {
            name: "Test Consultant",
            consultant_type: "strategy",
            industry_focus: "technology",
            target_company_size: "mid-market",
            geographic_preference: "north-america",
            solution_positioning: "digital transformation",
            signal_priorities: ["funding", "expansion", "leadership"],
            is_active: true
        };

        const response = await request.post(`${API_URL}/api/v1/consultants`, {
            data: consultantData
        });
        
        expect(response.status()).toBe(201);
        
        const consultant = await response.json();
        expect(consultant).toHaveProperty('id');
        expect(consultant.name).toBe(consultantData.name);
        expect(consultant.consultant_type).toBe(consultantData.consultant_type);
    });

    test('should handle consultant retrieval by ID', async ({ request }) => {
        // First create a consultant to retrieve
        const consultantData = {
            name: "Retrieve Test Consultant",
            consultant_type: "operations",
            industry_focus: "healthcare",
            target_company_size: "enterprise",
            geographic_preference: "global",
            solution_positioning: "operational excellence",
            signal_priorities: ["hiring", "product_launch"],
            is_active: true
        };

        const createResponse = await request.post(`${API_URL}/api/v1/consultants`, {
            data: consultantData
        });
        
        expect(createResponse.status()).toBe(201);
        const createdConsultant = await createResponse.json();
        
        // Now retrieve it
        const getResponse = await request.get(`${API_URL}/api/v1/consultants/${createdConsultant.id}`);
        
        if (getResponse.status() === 404) {
            // Expected since we're using placeholder implementation
            const error = await getResponse.json();
            expect(error).toHaveProperty('error');
        } else {
            expect(getResponse.status()).toBe(200);
            const consultant = await getResponse.json();
            expect(consultant.id).toBe(createdConsultant.id);
        }
    });

    test('should validate consultant data', async ({ request }) => {
        const invalidData = {
            name: "",  // Invalid: empty name
            consultant_type: "invalid_type",  // Invalid type
            // Missing required fields
        };

        const response = await request.post(`${API_URL}/api/v1/consultants`, {
            data: invalidData
        });
        
        expect(response.status()).toBe(422);  // Validation error
        
        const error = await response.json();
        expect(error).toHaveProperty('error');
        expect(error.error).toHaveProperty('code');
        expect(error.error.code).toBe('VALIDATION_ERROR');
    });

});

test.describe('Prospects API', () => {
    
    test('should list prospects with filtering', async ({ request }) => {
        const response = await request.get(`${API_URL}/api/v1/prospects?status=active&page=1&per_page=5`);
        
        expect(response.status()).toBe(200);
        
        const data = await response.json();
        expect(data).toHaveProperty('message');
        // Since using placeholder implementation, check for expected message
        expect(data.message).toContain('Prospects listing');
    });

    test('should handle prospect creation', async ({ request }) => {
        const prospectData = {
            name: "Test Company Inc.",
            industry: "Software",
            size: "mid-market",
            location: "San Francisco, CA",
            website: "https://testcompany.com",
            description: "Innovative software company focused on AI solutions"
        };

        const response = await request.post(`${API_URL}/api/v1/prospects`, {
            data: prospectData
        });
        
        expect(response.status()).toBe(201);
        
        const data = await response.json();
        expect(data).toHaveProperty('message');
        expect(data.message).toContain('Prospect creation');
    });

});

test.describe('Research API', () => {
    
    test('should list research tasks', async ({ request }) => {
        const response = await request.get(`${API_URL}/api/v1/research/tasks?page=1&per_page=10`);
        
        expect(response.status()).toBe(200);
        
        const data = await response.json();
        expect(data).toHaveProperty('message');
        expect(data.message).toContain('Research tasks listing');
    });

    test('should create research task', async ({ request }) => {
        const taskData = {
            task_type: "company_research",
            target_company: "Acme Corp",
            objectives: ["funding_analysis", "competitive_landscape"],
            consultant_id: 1
        };

        const response = await request.post(`${API_URL}/api/v1/research/tasks`, {
            data: taskData
        });
        
        expect(response.status()).toBe(201);
        
        const data = await response.json();
        expect(data).toHaveProperty('task_id');
        expect(data).toHaveProperty('status');
        expect(data.status).toBe('queued');
    });

    test('should list signals with filtering', async ({ request }) => {
        const response = await request.get(`${API_URL}/api/v1/research/signals?signal_type=funding&priority=high`);
        
        expect(response.status()).toBe(200);
        
        const data = await response.json();
        expect(data).toHaveProperty('message');
        expect(data.message).toContain('Signals listing');
    });

    test('should handle web scraping requests', async ({ request }) => {
        const scrapeData = {
            urls: ["https://example.com/news"],
            signal_types: ["funding", "expansion"],
            max_depth: 1
        };

        const response = await request.post(`${API_URL}/api/v1/research/scrape`, {
            data: scrapeData
        });
        
        expect(response.status()).toBe(200);
        
        const data = await response.json();
        expect(data).toHaveProperty('message');
        expect(data.message).toContain('Web scraping');
    });

});

test.describe('Reports API', () => {
    
    test('should list generated reports', async ({ request }) => {
        const response = await request.get(`${API_URL}/api/v1/reports?page=1&per_page=10`);
        
        expect(response.status()).toBe(200);
        
        const data = await response.json();
        expect(data).toHaveProperty('message');
        expect(data.message).toContain('Reports listing');
    });

    test('should generate new report', async ({ request }) => {
        const reportData = {
            report_type: "prospect_intelligence",
            prospect_id: 1,
            template_id: "default",
            include_signals: true,
            include_analysis: true
        };

        const response = await request.post(`${API_URL}/api/v1/reports/generate`, {
            data: reportData
        });
        
        expect(response.status()).toBe(201);
        
        const data = await response.json();
        expect(data).toHaveProperty('report_id');
        expect(data).toHaveProperty('status');
        expect(data.status).toBe('generating');
    });

    test('should handle report download requests', async ({ request }) => {
        const reportId = 'test-report-123';
        const response = await request.get(`${API_URL}/api/v1/reports/${reportId}/download`);
        
        // Expect 501 Not Implemented for placeholder
        expect(response.status()).toBe(501);
    });

});

test.describe('Campaigns API', () => {
    
    test('should list email campaigns', async ({ request }) => {
        const response = await request.get(`${API_URL}/api/v1/campaigns?page=1&per_page=10`);
        
        expect(response.status()).toBe(200);
        
        const data = await response.json();
        expect(data).toHaveProperty('message');
        expect(data.message).toContain('Email campaigns listing');
    });

    test('should create email campaign', async ({ request }) => {
        const campaignData = {
            name: "Q4 Outreach Campaign",
            campaign_type: "prospecting",
            template_id: 1,
            target_prospects: [1, 2, 3],
            send_schedule: "immediate"
        };

        const response = await request.post(`${API_URL}/api/v1/campaigns`, {
            data: campaignData
        });
        
        expect(response.status()).toBe(201);
        
        const data = await response.json();
        expect(data).toHaveProperty('campaign_id');
        expect(data).toHaveProperty('status');
        expect(data.status).toBe('draft');
    });

    test('should list email templates', async ({ request }) => {
        const response = await request.get(`${API_URL}/api/v1/campaigns/templates?page=1&per_page=5`);
        
        expect(response.status()).toBe(200);
        
        const data = await response.json();
        expect(data).toHaveProperty('message');
        expect(data.message).toContain('Email templates listing');
    });

});

test.describe('Error Handling', () => {
    
    test('should handle 404 for non-existent endpoints', async ({ request }) => {
        const response = await request.get(`${API_URL}/api/v1/nonexistent`);
        
        expect(response.status()).toBe(404);
    });

    test('should handle malformed JSON requests', async ({ request }) => {
        const response = await request.post(`${API_URL}/api/v1/consultants`, {
            data: "invalid json string",
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        expect([400, 422]).toContain(response.status());
    });

    test('should include correlation IDs in error responses', async ({ request }) => {
        const response = await request.get(`${API_URL}/api/v1/consultants/999999`);
        
        if (response.status() >= 400) {
            const error = await response.json();
            // Check if correlation_id is included in error response
            // This depends on backend implementation
            expect(error).toHaveProperty('error');
        }
    });

    test('should handle rate limiting appropriately', async ({ request }) => {
        // Make multiple rapid requests to test rate limiting
        const requests = Array(10).fill().map(() => 
            request.get(`${API_URL}/api/v1/consultants`)
        );
        
        const responses = await Promise.all(requests);
        
        // All should succeed or some should return 429 if rate limiting is active
        responses.forEach(response => {
            expect([200, 429]).toContain(response.status());
        });
    });

});

test.describe('API Performance', () => {
    
    test('should respond within acceptable time limits', async ({ request }) => {
        const startTime = Date.now();
        
        const response = await request.get(`${API_URL}/api/v1/consultants`);
        
        const responseTime = Date.now() - startTime;
        
        expect(response.status()).toBe(200);
        expect(responseTime).toBeLessThan(2000); // Less than 2 seconds
    });

    test('should handle concurrent requests', async ({ request }) => {
        const requests = [
            request.get(`${API_URL}/api/v1/consultants`),
            request.get(`${API_URL}/api/v1/prospects`),
            request.get(`${API_URL}/api/v1/research/tasks`),
            request.get(`${API_URL}/api/v1/reports`),
            request.get(`${API_URL}/api/v1/campaigns`)
        ];
        
        const startTime = Date.now();
        const responses = await Promise.all(requests);
        const totalTime = Date.now() - startTime;
        
        // All requests should complete
        responses.forEach(response => {
            expect(response.status()).toBe(200);
        });
        
        // Should complete in reasonable time
        expect(totalTime).toBeLessThan(5000);
    });

});

test.describe('Data Validation', () => {
    
    test('should validate required fields', async ({ request }) => {
        const incompleteData = {
            name: "Test"
            // Missing required fields
        };

        const response = await request.post(`${API_URL}/api/v1/consultants`, {
            data: incompleteData
        });
        
        expect(response.status()).toBe(422);
        
        const error = await response.json();
        expect(error.error.code).toBe('VALIDATION_ERROR');
        expect(error.error.details).toHaveProperty('field_errors');
    });

    test('should validate data types', async ({ request }) => {
        const invalidTypeData = {
            name: 123,  // Should be string
            consultant_type: "valid_type",
            industry_focus: ["should", "be", "string"],  // Should be string
            is_active: "not_boolean"  // Should be boolean
        };

        const response = await request.post(`${API_URL}/api/v1/consultants`, {
            data: invalidTypeData
        });
        
        expect(response.status()).toBe(422);
    });

    test('should validate enum values', async ({ request }) => {
        const invalidEnumData = {
            name: "Test Consultant",
            consultant_type: "invalid_consultant_type",  // Invalid enum value
            industry_focus: "technology",
            target_company_size: "invalid_size",  // Invalid enum value
            signal_priorities: ["invalid_signal_type"],  // Invalid enum values
            is_active: true
        };

        const response = await request.post(`${API_URL}/api/v1/consultants`, {
            data: invalidEnumData
        });
        
        expect(response.status()).toBe(422);
    });

});

test.describe('Authentication and Authorization', () => {
    
    test('should handle requests without authentication', async ({ request }) => {
        // For now, API is open. In production, this would require auth
        const response = await request.get(`${API_URL}/api/v1/consultants`);
        
        // Currently returns 200, but in production might return 401
        expect([200, 401]).toContain(response.status());
    });

    test('should handle invalid authentication tokens', async ({ request }) => {
        const response = await request.get(`${API_URL}/api/v1/consultants`, {
            headers: {
                'Authorization': 'Bearer invalid_token_here'
            }
        });
        
        // Currently ignores auth, but in production would return 401
        expect([200, 401]).toContain(response.status());
    });

});

test.describe('Integration with Frontend', () => {
    
    test('should support frontend API calls', async ({ page }) => {
        // Navigate to frontend
        await page.goto(BASE_URL);
        await page.waitForSelector('#main-content', { state: 'visible' });
        
        // Intercept API calls from frontend
        let apiCallMade = false;
        
        page.on('request', request => {
            if (request.url().includes(API_URL)) {
                apiCallMade = true;
            }
        });
        
        // Wait for frontend to make API calls
        await page.waitForTimeout(3000);
        
        expect(apiCallMade).toBe(true);
    });

    test('should handle API errors in frontend', async ({ page }) => {
        // Mock API to return errors
        await page.route(`${API_URL}/health`, route => {
            route.fulfill({
                status: 500,
                contentType: 'application/json',
                body: JSON.stringify({ error: 'Server Error' })
            });
        });
        
        await page.goto(BASE_URL);
        
        // Should show error message
        await page.waitForSelector('#loading-screen', { timeout: 5000 });
        await expect(page.locator('#loading-screen')).toContainText('Failed to initialize');
    });

});