#!/usr/bin/env node
// Export an HTML page (URL or local file) to PNG at exact pixel size with Playwright.
// Usage: node screenshot.mjs --url <url|file> --width 1500 --height 500 --output out.png [--scale 2]
// Browser: $CHROME_PATH, else the newest ~/.cache/ms-playwright chromium, else Playwright's default.
import { chromium } from 'playwright-core';
import { existsSync, readdirSync, mkdirSync } from 'node:fs';
import { dirname, resolve, join } from 'node:path';
import { homedir } from 'node:os';
import { pathToFileURL } from 'node:url';

const a = {}; const argv = process.argv.slice(2);
for (let i = 0; i < argv.length; i += 2) a[argv[i].replace(/^--/, '')] = argv[i + 1];
if (!a.url || !a.width || !a.height || !a.output) {
  console.error('usage: --url <url|file> --width N --height N --output out.png [--scale 2]'); process.exit(2);
}
function browserPath() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const base = join(homedir(), '.cache', 'ms-playwright');
  if (!existsSync(base)) return undefined;
  const dirs = readdirSync(base).filter(d => d.startsWith('chromium-')).sort().reverse();
  for (const d of dirs) for (const sub of ['chrome-linux64/chrome', 'chrome-linux/chrome', 'chrome-mac/Chromium.app/Contents/MacOS/Chromium', 'chrome-win/chrome.exe']) {
    const p = join(base, d, sub); if (existsSync(p)) return p;
  }
}
const url = /^[a-z]+:\/\//i.test(a.url) ? a.url : pathToFileURL(resolve(a.url)).href;
const browser = await chromium.launch({ executablePath: browserPath() });
const page = await browser.newPage({ viewport: { width: +a.width, height: +a.height }, deviceScaleFactor: +(a.scale || 2) });
await page.goto(url, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts && document.fonts.ready);
mkdirSync(dirname(resolve(a.output)), { recursive: true });
await page.screenshot({ path: a.output, clip: { x: 0, y: 0, width: +a.width, height: +a.height } });
await browser.close();
console.log(`saved ${a.output} (${a.width}x${a.height} @${a.scale || 2}x)`);
