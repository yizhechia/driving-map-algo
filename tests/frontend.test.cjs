/* Actual app.js against the actual HTTP API, with a small DOM/canvas test double.
 * This checks interaction logic, not browser rendering, CSS, or native downloads.
 * Run: node --test tests/frontend.test.cjs (Node >=18, Python >=3.10).
 */
const assert = require('node:assert/strict');
const { before, after, test } = require('node:test');
const { spawn } = require('node:child_process');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const html = readFileSync(path.join(root, 'commute_map/static/index.html'), 'utf8');
const source = readFileSync(path.join(root, 'commute_map/static/app.js'), 'utf8');
let server, base;

before(async () => {
  server = spawn(process.env.PYTHON || 'python', ['-u', '-m', 'commute_map', 'serve', '--port', '0'],
    { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
  base = await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(Error('Demo server did not start')), 10000);
    let output = '';
    server.stdout.on('data', chunk => {
      output += chunk;
      const match = output.match(/Commute Lab: (http:\/\/127\.0\.0\.1:\d+)/);
      if (match) { clearTimeout(timeout); resolve(match[1]); }
    });
    server.once('error', error => { clearTimeout(timeout); reject(error); });
    server.once('exit', code => { clearTimeout(timeout); reject(Error(`Server exited: ${code}`)); });
  });
});
after(() => { if (server) server.kill(); });

class Element {
  constructor(tag = 'div') {
    this.tagName = tag; this.children = []; this.listeners = {}; this.dataset = {};
    this.value = ''; this.disabled = false; this.hidden = false; this.className = ''; this.text = '';
    this.classList = { toggle: (name, active) => {
      const classes = new Set(this.className.split(' ').filter(Boolean));
      active ? classes.add(name) : classes.delete(name); this.className = [...classes].join(' ');
    }};
  }
  set textContent(value) { this.text = String(value); this.children = []; }
  get textContent() { return this.text + this.children.map(child => child.textContent).join(''); }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.text = ''; this.children = children; }
  addEventListener(type, handler) { (this.listeners[type] ||= []).push(handler); }
  async fire(type, event = {}) {
    for (const handler of this.listeners[type] || []) await handler({ preventDefault() {}, ...event });
  }
  click() { return this.fire('click'); }
  getBoundingClientRect() { return { left: 0, top: 0, width: this.width, height: this.height }; }
}

async function harness() {
  const elements = {}, requests = [], downloads = [], pending = [];
  for (const match of html.matchAll(/<(\w+)\b([^>]*\bid="([^"]+)"[^>]*)>/g)) {
    const [, tag, attrs, id] = match, element = new Element(tag);
    element.value = attrs.match(/\bvalue="([^"]*)"/)?.[1] || '';
    element.disabled = /\bdisabled\b/.test(attrs); element.hidden = /\bhidden\b/.test(attrs);
    if (tag === 'select') {
      const body = html.slice(match.index + match[0].length).split('</select>')[0];
      const options = [...body.matchAll(/<option value="([^"]+)"([^>]*)>/g)];
      element.value = (options.find(item => /\bselected\b/.test(item[2])) || options[0])[1];
    }
    elements[id] = element;
  }
  const canvas = elements.map;
  canvas.width = 900; canvas.height = 690;
  let drawCalls = 0;
  canvas.getContext = () => new Proxy({}, { get: (_, method) => {
    if (method === 'measureText') return text => ({ width: text.length * 7 });
    return (...args) => {
      for (const arg of args) if (typeof arg === 'number') assert.ok(Number.isFinite(arg));
      drawCalls++;
    };
  }});
  function descendants(node) { return [node, ...node.children.flatMap(descendants)]; }
  const document = {
    getElementById: id => elements[id],
    querySelectorAll: selector => {
      assert.equal(selector, '.card');
      return descendants(elements.cards).filter(item => item.className.split(' ').includes('card'));
    },
    createElement: tag => {
      const node = new Element(tag);
      if (tag === 'a') node.click = () => downloads.push(node);
      return node;
    }
  };
  let holdNext = null, failNext = false, release = null;
  const context = vm.createContext({ document, Blob, console,
    URL: { createObjectURL: blob => { downloads.push(blob); return 'blob:unit-test'; }, revokeObjectURL() {} },
    fetch: async (url, options) => {
      requests.push({ url, body: JSON.parse(options.body) });
      const task = (async () => {
        if (holdNext === url) {
          holdNext = null;
          await new Promise(resolve => { release = resolve; });
        }
        if (failNext) { failNext = false; throw Error('Simulated connection failure'); }
        return fetch(base + url, options);
      })();
      pending.push(task);
      return task;
    }
  });
  vm.runInContext(source, context, { filename: 'app.js' });
  // Await app.js's initial request and the actual response processing.
  await pending[0];
  for (let attempt = 0; elements.run.disabled && attempt < 500; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 2));
  }
  assert.equal(elements.run.disabled, false, 'Initial rendering should finish');
  assert.ok(drawCalls > 0, 'The canvas drawing path should execute');
  return {
    elements, requests, downloads,
    change: async (id, value) => { elements[id].value = String(value); await elements.settings.fire('input'); },
    update: () => elements.settings.fire('submit'),
    card: id => elements.cards.children.find(item => item.dataset.id === id),
    hold: url => { holdNext = url; },
    release: () => { assert.ok(release); release(); release = null; },
    fail: () => { failNext = true; }
  };
}

test('initial render, corridor/local examples, condo overhead, and direction', async () => {
  const h = await harness(), e = h.elements;
  assert.equal(e.cards.children.length, 6);
  assert.match(h.card('SB_HOUSE').textContent, /54\.0/);
  assert.match(h.card('RAWANG_HOUSE').textContent, /47\.6/);
  assert.equal(e.download.disabled, false);
  await h.change('buffer', 0); await h.update();
  assert.match(h.card('SB_HOUSE').textContent, /48\.0/);
  assert.match(h.card('RAWANG_HOUSE').textContent, /Within limit40\.0/);
  await h.card('CHERAS_CONDO').click();
  assert.match(e.detail.textContent, /31\.0/);
  assert.match(e.detail.textContent, /Home access5\.0 min/);
  await h.change('direction', 'home_to_work'); await h.update();
  assert.match(e['map-heading'].textContent, /Home → KLCC/);
  assert.match(h.card('SB_HOUSE').textContent, /52\.0/);
});

test('sparse sampling, no route, and zero budget retain distinct states', async () => {
  const h = await harness(), e = h.elements;
  await h.card('ISOLATED').click();
  assert.match(e.detail.textContent, /No route in this model/);
  await h.change('method', 'adaptive'); await h.change('budget', 64); await h.update();
  assert.equal(e.budget.disabled, false);
  assert.equal(h.requests.at(-1).body.budget, 64);
  assert.match(e.coverage.textContent, /64 \/ 1,024/);
  await h.change('budget', 0); await h.update();
  assert.match(e.coverage.textContent, /1024 unknown/);
  await e.map.fire('click', { clientX: 430, clientY: 330 });
  assert.match(e.detail.textContent, /Not directly sampled/);
  assert.match(e.detail.textContent, /not queried/);
});

test('64x64 grid and assumed morning profile render through the same interface', async () => {
  const h = await harness();
  await h.change('size', 64); await h.change('period', 'morning'); await h.update();
  assert.equal(h.requests.at(-1).body.budget, 4096);
  assert.match(h.elements.coverage.textContent, /4,096 \/ 4,096/);
  assert.match(h.card('SB_HOUSE').textContent, /57\.3/);
});

test('editing settings during a calculation cannot mark an old result as current', async () => {
  const h = await harness(), e = h.elements;
  h.hold('/api/run'); const updating = h.update();
  await h.change('threshold', 60); h.release(); await updating;
  assert.match(e['map-heading'].textContent, /45\.0 min/);
  assert.match(e['run-status'].textContent, /Settings changed/);
  assert.equal(e.download.disabled, true);
  await h.update();
  assert.match(e['map-heading'].textContent, /60\.0 min/);
  assert.equal(e.download.disabled, false);
});

test('export uses displayed settings, preserves provenance, and handles concurrent edits', async () => {
  const h = await harness(), e = h.elements;
  h.hold('/api/export'); const exporting = e.download.fire('click');
  await h.change('threshold', 60); h.release(); await exporting;
  assert.equal(h.requests.at(-1).body.threshold, 45);
  const exported = JSON.parse(await h.downloads[0].text());
  assert.equal(exported.type, 'FeatureCollection');
  assert.equal(exported.manifest.source, 'synthetic_kl_v1');
  assert.equal(h.downloads[1].download, 'synthetic-commute-region.geojson');
  assert.equal(e.download.disabled, true);
});

test('API validation and failed connection show an error and recover on the next run', async () => {
  const h = await harness(), e = h.elements;
  await h.change('threshold', -1); await h.update();
  assert.equal(e.error.hidden, false);
  assert.match(e['run-status'].textContent, /previous result/);
  assert.equal(e.run.disabled, false);
  await h.change('threshold', 60); h.fail(); await h.update();
  assert.match(e.error.textContent, /Simulated connection failure/);
  await h.update();
  assert.equal(e.error.hidden, true);
  assert.match(e['map-heading'].textContent, /60\.0 min/);
});
