import { test, expect } from '@playwright/test';

test('should register, login and manage tasks', async ({ page }) => {
  // Идём на главную (перенаправит на login)
  await page.goto('http://localhost:80');  // или ваш dev-сервер

  // Регистрация нового пользователя
  await page.click('text=Зарегистрироваться');
  await page.fill('#username', 'testuser');
  await page.fill('#password', 'testpass');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/login/);

  // Логин
  await page.fill('#username', 'testuser');
  await page.fill('#password', 'testpass');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/index/);

  // Создание задачи
  await page.fill('#title', 'Тестовая задача');
  await page.click('#taskForm button[type="submit"]');
  await expect(page.locator('.task-title')).toHaveText('Тестовая задача');

  // Поиск
  await page.fill('#searchInput', 'Тестовая');
  await expect(page.locator('.task-title')).toHaveCount(1);

  // Отметить выполненной
  await page.check('input[type="checkbox"]');
  // Проверить, что появилось зачёркивание
  await expect(page.locator('.completed')).toHaveCount(1);
});