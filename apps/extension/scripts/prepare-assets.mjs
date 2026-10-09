import { mkdir, writeFile, access } from 'node:fs/promises';
import { createWriteStream } from 'node:fs';
import { pipeline } from 'node:stream/promises';
import { Readable } from 'node:stream';
const out='public/tesseract'; await mkdir(out,{recursive:true});
const urls={
  'worker.min.js':process.env.TESSERACT_WORKER_URL||'https://cdn.jsdelivr.net/npm/tesseract.js@6.0.1/dist/worker.min.js',
  'tesseract-core.wasm.js':process.env.TESSERACT_CORE_URL||'https://cdn.jsdelivr.net/npm/tesseract.js-core@6.0.0/tesseract-core.wasm.js',
  'eng.traineddata.gz':process.env.TESSDATA_ENG_URL||'https://tessdata.projectnaptha.com/4.0.0/eng.traineddata.gz',
  'ben.traineddata.gz':process.env.TESSDATA_BEN_URL||'https://tessdata.projectnaptha.com/4.0.0/ben.traineddata.gz'
};
for(const [name,url] of Object.entries(urls)){
  try { await access(`${out}/${name}`); console.log('Exists',name); continue; } catch {}
  const r=await fetch(url); if(!r.ok) throw new Error(`Failed to fetch ${url}: ${r.status}`);
  await pipeline(Readable.fromWeb(r.body),createWriteStream(`${out}/${name}`)); console.log('Fetched',name);
}
await writeFile(`${out}/assets.lock.json`,JSON.stringify({version:1,assets:Object.entries(urls).map(([name,url])=>({name,url}))},null,2)+'\n');
console.log('Tesseract assets ready.');
