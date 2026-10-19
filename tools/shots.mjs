// Screenshot every page after each tap, to check the animations land where they should.
// Usage: node tools/shots.mjs <outDir> [pages...]
import { spawn } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9334;
const OUT = process.argv[2] || '/tmp/rl_shots';
const PAGES = process.argv.slice(3);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
fs.mkdirSync(OUT, { recursive: true });

const profile = fs.mkdtempSync('/tmp/rl-shots-');
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`, '--window-size=1194,834',
  '--hide-scrollbars', '--no-first-run', `--user-data-dir=${profile}`, 'about:blank'], { stdio: 'ignore' });

let ws, id = 0;
const pending = new Map();
const send = (method, params = {}, sessionId) => {
  const msg = { id: ++id, method, params, ...(sessionId ? { sessionId } : {}) };
  ws.send(JSON.stringify(msg));
  return new Promise((res, rej) => pending.set(msg.id, { res, rej }));
};

async function main() {
  let info;
  for (let i = 0; i < 50 && !info; i++) {
    try { info = await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json(); } catch { await sleep(200); }
  }
  ws = new WebSocket(info.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));
  ws.addEventListener('message', (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
  });
  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId: s } = await send('Target.attachToTarget', { targetId, flatten: true });
  await send('Emulation.setDeviceMetricsOverride', { width: 1194, height: 834, deviceScaleFactor: 1, mobile: false }, s);
  const shot = async (file) => {
    const { data } = await send('Page.captureScreenshot', { format: 'png' }, s);
    fs.writeFileSync(path.join(OUT, file), Buffer.from(data, 'base64'));
  };
  for (const name of PAGES) {
    await send('Page.navigate', { url: pathToFileURL(path.join(ROOT, name + '.html')).href + '?solo' }, s);
    await sleep(2000);
    await shot(`${name}-s0.png`);
    const { result } = await send('Runtime.evaluate', { returnByValue: true, expression:
      `(() => { const m = document.body.innerHTML.match(/durs = \\[([^\\]]*)\\]/); return m ? m[1].split(',').map(Number) : [1700]; })()` }, s);
    const durs = result.value;
    const taps = Math.max(1, durs.length - 1);
    for (let k = 1; k <= taps; k++) {
      await send('Runtime.evaluate', { expression: `document.querySelector('#dc-root button').click()` }, s);
      await sleep((durs[k] || 1700) + 600);
      await shot(`${name}-s${k}.png`);
    }
    console.log(name, durs.length);
  }
}
main().catch((e) => { console.error(e); process.exitCode = 1; }).finally(() => { try { ws?.close(); } catch {} chrome.kill(); });
