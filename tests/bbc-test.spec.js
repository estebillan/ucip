import { test, expect } from '@playwright/test';

test('navigate to bbc.com', async ({ page }) => {
  // Navigate to BBC website
  await page.goto('https://www.bbc.com');
  
  // Wait for page to load and verify we're on BBC
  await expect(page).toHaveTitle(/BBC/);
  
  // Take a screenshot for verification
  await page.screenshot({ path: 'bbc-screenshot.png' });
  
  console.log('Successfully navigated to BBC.com');
});