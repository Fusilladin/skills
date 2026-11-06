const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const errs = [], ext = [];
  for (const [w, h] of [[1440, 900], [390, 844]]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    p.on('console', m => m.type() === 'error' && errs.push(w + ': ' + m.text()));
    p.on('pageerror', e => errs.push(w + ': ' + e.message));
    p.on('request', r => { if (!r.url().startsWith('file:')) ext.push(r.url()); });
    await p.goto('file://' + process.argv[2]);
    for (let y = 0; y < 12000; y += 600) { await p.evaluate(y => window.scrollTo({ top: y, behavior: 'instant' }), y); await p.waitForTimeout(120); }
    await p.waitForTimeout(800);
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    console.log(w, 'overflow', ov);
    
    await p.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
    await p.screenshot({ path: process.argv[3] + '-' + w + '.png', fullPage: true });
  }
  console.log('errors', errs, 'external', ext);
  await b.close();
})();
