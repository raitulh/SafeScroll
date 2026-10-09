import { access, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('..', import.meta.url));
const required=['README.md','.env.example','apps/extension/public/models/scam-classifier/model.json','apps/extension/public/tesseract/README.txt','apps/api/app/services/web_risk.py','apps/api/app/services/rules_signing.py','infra/terraform/main.tf'];
for(const f of required){try{await access(path.join(root,f))}catch{throw new Error(`Missing release file: ${f}`)}}
const manifest=JSON.parse(await readFile(path.join(root,'apps/extension/manifest.json'),'utf8'));
if(manifest.manifest_version!==3||manifest.action.default_popup!=='index.html'||manifest.background.service_worker!=='background.js'||manifest.host_permissions)throw new Error('Invalid MV3 release manifest');
console.log('SafeScroll release checks passed.');
