import { test, expect } from '@playwright/test';
test('landing page renders the safety value proposition', async ({page})=>{
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /Before you click/i })).toBeVisible();
  await expect(page.getByText(/privacy-first/i).first()).toBeVisible();
});
test('privacy page exists', async ({page})=>{await page.goto('/privacy');await expect(page).toHaveURL(/privacy/);});
