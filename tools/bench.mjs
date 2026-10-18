// Frame-rate benchmark for every page, run in headless Chrome over the DevTools protocol.
// Usage: node tools/bench.mjs [cpuThrottle=4] [pages...]
// Emulates a slower device (CPU throttling + software rendering), taps the scene a few
// times like a child would, and reports presented frames per second from the trace.
import { spawn } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9333;
const THROTTLE = Number(process.argv[2] || 4);
const ALL = ['index', 'p02-training', 'p03-suit-up', 'p04-rollout', 'p05-fuel', 'p06-board', 'p07-countdown',
  'p08-liftoff', 'p09-booster', 'p10-refuel', 'p11-journey', 'p12-landing', 'p13-moonwalk', 'p14-home'];
const PAGES = process.argv.length > 3 ? process.argv.slice(3) : ALL;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const profile = fs.mkdtempSync('/tmp/rl-bench-');
const chrome = spawn(CHROME, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${PORT}`,
  '--window-size=1194,834', '--hide-scrollbars', '--no-first-run', `--user-data-dir=${profile}`, 'about:blank'],
  { stdio: 'ignore' });

let ws, id = 0;
const pending = new Map(), listeners = [];
function send(method, params = {}, sessionId) {
  const msg = { id: ++id, method, params };
  if (sessionId) msg.sessionId = sessionId;
  ws.send(JSON.stringify(msg));
  return new Promise((res, rej) => pending.set(msg.id, { res, rej }));
}

async function main() {
  let info;
  for (let i = 0; i < 50 && !info; i++) {
    try { info = await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json(); } catch { await sleep(200); }
  }
  ws = new WebSocket(info.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));
  ws.addEventListener('message', (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const p = pending.get(m.id); pending.delete(m.id);
      m.error ? p.rej(new Error(m.error.message)) : p.res(m.result);
    } else listeners.forEach((l) => l(m));
  });
  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId: s } = await send('Target.attachToTarget', { targetId, flatten: true });
  await send('Page.enable', {}, s);
  await send('Emulation.setDeviceMetricsOverride', { width: 1194, height: 834, deviceScaleFactor: 2, mobile: false }, s);
  await send('Emulation.setCPUThrottlingRate', { rate: THROTTLE }, s);

  const rows = [];
  for (const name of PAGES) {
    const url = pathToFileURL(path.join(ROOT, name + '.html')).href;
    await send('Page.navigate', { url }, s);
    await sleep(2500);
    if (process.env.PRE_EVAL) { await send('Runtime.evaluate', { expression: process.env.PRE_EVAL }, s); await sleep(300); }
    if (process.env.LAYERS) {
      let layers = [];
      const onL = (m) => { if (m.method === 'LayerTree.layerTreeDidChange' && m.params.layers) layers = m.params.layers; };
      listeners.push(onL);
      await send('LayerTree.enable', {}, s); await sleep(800);
      for (const l of layers) {
        let why = [];
        try { why = (await send('LayerTree.compositingReasons', { layerId: l.layerId }, s)).compositingReasonIds || []; } catch {}
        console.log(name, l.layerId, Math.round(l.width) + 'x' + Math.round(l.height), l.drawsContent ? 'draws' : '', why.join(','));
      }
      await send('LayerTree.disable', {}, s);
      listeners.splice(listeners.indexOf(onL), 1);
    }

    const events = [];
    const onMsg = (m) => { if (m.method === 'Tracing.dataCollected') events.push(...m.params.value); };
    listeners.push(onMsg);
    const done = new Promise((r) => listeners.push((m) => { if (m.method === 'Tracing.tracingComplete') r(); }));
    await send('Tracing.start', { categories: process.env.CATS || 'devtools.timeline,benchmark,disabled-by-default-devtools.timeline.frame', transferMode: 'ReportEvents' }, s);
    // Tap the scene every 1.8s (most animations play on tap) while the idle loops keep running.
    const r = await send('Runtime.evaluate', {
      awaitPromise: true, returnByValue: true, expression: `(async () => {
        const btn = document.querySelector('#dc-root button, #dc-root [role=button]');
        const t = []; let run = true;
        (function f(x) { t.push(x); if (run) requestAnimationFrame(f); })(performance.now());
        for (let i = 0; i < 4; i++) { if (btn) btn.click(); await new Promise(r => setTimeout(r, 1800)); }
        run = false;
        const d = t.slice(1).map((x, i) => x - t[i]).sort((a, b) => a - b);
        return { raf: Math.round(1000 * d.length / (t[t.length - 1] - t[0])), p95: Math.round(d[Math.floor(d.length * .95)]) };
      })()` }, s);
    await send('Tracing.end', {}, s);
    await done;
    listeners.splice(listeners.indexOf(onMsg), 1);

    // Presented frames come from the compositor; dropped ones never reach the screen.
    const pr = events.filter((e) => e.name === 'PipelineReporter' && e.ph === 'b');
    const states = {};
    for (const e of pr) { const st = e.args?.chrome_frame_reporter?.state || e.args?.data?.state || '?'; states[st] = (states[st] || 0) + 1; }
    const presented = (states.STATE_PRESENTED_ALL || 0) + (states.STATE_PRESENTED_PARTIAL || 0);
    const dropped = states.STATE_DROPPED || 0;
    const ts = events.filter((e) => e.ts).map((e) => e.ts);
    const secs = (Math.max(...ts) - Math.min(...ts)) / 1e6;
    const raster = events.filter((e) => e.name === 'RasterTask' && e.dur).reduce((a, e) => a + e.dur, 0) / 1000;
    const by = {};
    for (const e of events) if (e.ph === 'X' && e.dur) by[e.name] = (by[e.name] || 0) + e.dur / 1000;
    const top = Object.entries(by).sort((a, b) => b[1] - a[1]).slice(0, 14).map(([k, v]) => k + ':' + Math.round(v / secs)).join(' ');
    if (process.env.BREAKDOWN) console.log(name, 'ms/s ->', top);
    rows.push({ page: name, ...r.result.value, presentedFps: Math.round(presented / secs), dropped, rasterMsPerSec: Math.round(raster / secs) });
    console.log(JSON.stringify(rows[rows.length - 1]));
  }
  console.table(rows);
}

main().catch((e) => { console.error(e); process.exitCode = 1; }).finally(() => { try { ws?.close(); } catch {} chrome.kill(); });
