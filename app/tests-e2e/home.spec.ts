import { test, expect } from '@playwright/test';

test.describe('Gametime E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test('root page loads successfully', async ({ page }) => {
    await expect(page).toHaveTitle(/Root Page/);
    await expect(page.locator('h1')).toContainText('Welcome to the Root Page');
  });

  test('navigate to phone form from root page', async ({ page }) => {
    // Click the link to phone form
    await page.click('a[href="/game-monitor/phone-form/"]');
    
    // Should be on phone form page
    await expect(page).toHaveURL(/.*phone-form/);
  });

  test('phone form page loads with correct elements', async ({ page }) => {
    await page.goto('/game-monitor/phone-form/');
    
    // Check for form elements
    await expect(page.locator('form')).toBeVisible();
    await expect(page.locator('input[name="phone_number"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('submit valid phone number', async ({ page }) => {
    await page.goto('/game-monitor/phone-form/');
    
    // Fill in valid phone number
    await page.fill('input[name="phone_number"]', '+15555555555');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should redirect to success page
    await expect(page).toHaveURL(/.*success/);
    await expect(page.locator('body')).toContainText('Success');
  });

  test('submit invalid phone number shows error', async ({ page }) => {
    await page.goto('/game-monitor/phone-form/');
    
    // Fill in invalid phone number
    await page.fill('input[name="phone_number"]', 'invalid');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should show error message
    await expect(page.locator('.errorlist')).toBeVisible();
    await expect(page.locator('.errorlist')).toContainText('Enter a valid phone number');
  });

  test('success page displays correctly', async ({ page }) => {
    await page.goto('/game-monitor/success/');
    
    await expect(page.locator('body')).toContainText('Success');
  });

  test('games page loads with game data', async ({ page }) => {
    await page.goto('/games/');
    
    // Check that games are displayed
    await expect(page.locator('h1')).toContainText('NBA Games');
  });

  test('API endpoint returns close games', async ({ request }) => {
    const response = await request.get('/game-monitor/mock-api/');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('close_games');
    expect(Array.isArray(data.close_games)).toBeTruthy();
  });

  test('cache API endpoint works', async ({ request }) => {
    const response = await request.get('/game-monitor/test-cache/');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('data');
    expect(data).toHaveProperty('fetch_source');
    expect(data).toHaveProperty('elapsed_time');
  });

  test('handle non-existent pages gracefully', async ({ page }) => {
    const response = await page.goto('/non-existent-page/');
    expect(response?.status()).toBe(404);
  });
});