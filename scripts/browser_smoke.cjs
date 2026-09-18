'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const {spawn} = require('node:child_process');
const {chromium} = require('playwright');
const base = 'http://127.0.0.1:8765';
const server = spawn(process.env.PYTHON || 'python',['-m','commute_map','serve','--port','8765'],{stdio:['ignore','pipe','pipe']});
let browser;
const delay = ms => new Promise(resolve=>setTimeout(resolve,ms));
async function updated(page) {
  await page.waitForFunction(()=>document.getElementById('run-status').textContent==='Updated · synthetic scenario');
}
async function apply(page) {
  await page.locator('#run').click();
  await updated(page);
}
async function card(page,id,text) {
  assert.match(await page.locator('.card[data-id="'+id+'"]').innerText(),new RegExp(text));
}
(async()=>{
  try {
    await fs.mkdir('browser-artifacts',{recursive:true});
    let ready=false;
    for(let i=0;i<120;i++){
      try {const r=await fetch(base+'/health');if(r.ok){ready=true;break;}}catch{}
      await delay(100);
    }
    assert(ready,'local server did not start');
    browser=await chromium.launch({headless:true});
    const page=await browser.newPage({viewport:{width:1440,height:1000}});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.goto(base);
    await updated(page);
    assert.equal(await page.locator('.card').count(),6);
    await card(page,'SB_HOUSE','54.0');
    await card(page,'RAWANG_HOUSE','47.6');
    await page.screenshot({path:'browser-artifacts/desktop.png',fullPage:true});

    await page.locator('#buffer').fill('0');await apply(page);
    await card(page,'SB_HOUSE','48.0');
    await card(page,'RAWANG_HOUSE','40.0');
    await card(page,'CHERAS_CONDO','31.0');
    await page.locator('.card[data-id="CHERAS_CONDO"]').click();
    assert.match(await page.locator('#detail').innerText(),/Home access/);
    await page.locator('#condo').fill('0');await apply(page);
    await card(page,'CHERAS_CONDO','26.0');

    await page.locator('#direction').selectOption('home_to_work');await apply(page);
    await card(page,'SB_HOUSE','52.0');
    await page.locator('#period').selectOption('morning');await apply(page);
    await card(page,'SB_HOUSE','66.7');

    await page.locator('summary').click();
    await page.locator('#size').selectOption('64');await apply(page);
    assert.match(await page.locator('#coverage').innerText(),/4,096 \/ 4,096/);
    await page.locator('#method').selectOption('adaptive');
    await page.locator('#budget').fill('0');await apply(page);
    assert.match(await page.locator('#coverage').innerText(),/4096 unknown/);
    await page.locator('#size').selectOption('16');
    await page.locator('#method').selectOption('uniform');
    await page.locator('#budget').fill('64');await apply(page);
    assert.match(await page.locator('#coverage').innerText(),/64 \/ 256/);
    await page.locator('#method').selectOption('full');
    await page.locator('#direction').selectOption('work_to_home');
    await page.locator('#period').selectOption('example');await apply(page);
    await page.locator('#map').click({position:{x:200,y:200}});
    assert.match(await page.locator('#detail h2').innerText(),/Access/);

    const downloadPromise=page.waitForEvent('download');
    await page.locator('#download').click();
    const download=await downloadPromise;
    await download.saveAs('browser-artifacts/region.geojson');
    const geo=JSON.parse(await fs.readFile('browser-artifacts/region.geojson','utf8'));
    assert.equal(geo.type,'FeatureCollection');
    assert.match(geo.data_source,/Synthetic/);

    await page.route('**/api/run',async route=>{await delay(300);await route.continue();});
    await page.locator('#threshold').fill('47');
    await page.locator('#run').click();
    await page.locator('#threshold').fill('49');
    await page.waitForFunction(()=>!document.getElementById('run').disabled);
    assert.match(await page.locator('#run-status').innerText(),/Settings changed/);
    assert.equal(await page.locator('#download').isDisabled(),true);
    await page.unroute('**/api/run');
    await apply(page);

    await page.route('**/api/run',route=>route.abort());
    await page.locator('#threshold').fill('50');
    await page.locator('#run').click();
    await page.locator('#error').waitFor({state:'visible'});
    assert.equal(await page.locator('#run').isEnabled(),true);
    assert.match(await page.locator('#map-heading').innerText(),/49.0/);
    await page.unroute('**/api/run');await apply(page);
    assert.equal(await page.locator('#error').isVisible(),false);

    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:'browser-artifacts/mobile.png',fullPage:true});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),'mobile horizontal overflow');
    assert.deepEqual(errors,[],'uncaught browser exceptions');
    console.log('Browser checks passed: examples, controls, directions, profiles, grid sizes, sampling, cell inspection, export, request failure/recovery, edit-during-request, mobile overflow; zero uncaught browser exceptions.');
  } finally {
    if(browser)await browser.close();
    server.kill('SIGTERM');
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
