const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
let browser;

(async () => {
  const base = process.argv[2] || 'http://127.0.0.1:8765';
  const root = path.resolve(__dirname, '..');
  const category = fs.readFileSync(path.join(root, 'men-casual-shirts.html'), 'utf8');
  const pages = [...category.matchAll(/<a class="product-card au-card[^\"]*" href="([^\"]+)"/g)].map(m => m[1]);
  browser = await chromium.launch({ headless: true, ...(process.env.BROWSER_EXECUTABLE ? { executablePath: process.env.BROWSER_EXECUTABLE } : {}) });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  let colors = 0;
  for (const file of pages) {
    await page.goto(`${base}/${file}`, { waitUntil: 'domcontentloaded' });
    await page.locator('[data-gallery-status]').filter({ hasText: '/' }).waitFor();
    const options = await page.locator('#opt-color option').evaluateAll(os => os.map(o => o.value).filter(Boolean));
    for (const color of options) {
      await page.locator('#opt-color').selectOption(color);
      const photos = await page.locator('.pdp-thumb:visible').evaluateAll(ts => ts.map(t => ({ color: t.dataset.colour, src: t.dataset.src, label: t.dataset.label })));
      assert(photos.length > 0, `${file} ${color}: no photos`);
      assert(photos.every(p => p.color === color), `${file} ${color}: mixed color set`);
      assert.equal(await page.locator('#pdpMain').getAttribute('src'), photos[0].src);
      for (let index = 0; index < photos.length; index++) {
        assert.equal(await page.locator('#pdpMain').getAttribute('src'), photos[index].src);
        assert.equal(await page.locator('[data-gallery-status]').innerText(), `${color} · ${index + 1} / ${photos.length}`);
        assert(fs.existsSync(path.join(root, photos[index].src)), 'Missing gallery asset');
        if (photos.length > 1) await page.locator('[data-gallery-next]').click();
        else assert(await page.locator('[data-gallery-next]').isDisabled());
      }
      assert.equal(await page.locator('#pdpMain').getAttribute('src'), photos[0].src, 'Next wraps within selected color');
      if (photos.length > 1) await page.locator('[data-gallery-prev]').click();
      assert.equal(await page.locator('#pdpMain').getAttribute('src'), photos.at(-1).src, 'Previous wraps within selected color');
      const modelPhotos = photos.filter(p => p.src.includes('/gioberti-studio/'));
      assert.deepEqual(photos.slice(0, modelPhotos.length), modelPhotos, 'Model photos precede product photos');
      if (process.argv.includes('--complete')) assert.deepEqual(modelPhotos.map(p => path.basename(p.src)), ['front.webp', 'threequarter.webp', 'back.webp'], `${file} ${color}: expected three ordered model views`);
      colors++;
    }
    await page.locator('#opt-color').selectOption('');
    assert.equal(await page.locator('.pdp-thumb:visible').count(), 0, 'No color chosen hides all sets');
    await page.locator('#opt-color').selectOption(options[0]);
    await page.setViewportSize({ width: 390, height: 844 });
    assert(await page.locator('#pdpMain').isVisible());
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'Mobile horizontal overflow');
    await page.setViewportSize({ width: 1440, height: 1000 });
  }
  assert.equal(pages.length, 8);
  assert.equal(colors, 92);
  assert.deepEqual(errors, []);
  console.log(`Verified ${pages.length} shirt pages and ${colors} color galleries: isolated photos, model-first ordering, navigation, missing files, mobile layout, and no script errors.`);
  await browser.close();
})().catch(async error => { console.error(error); if (browser) await browser.close(); process.exitCode = 1; });
