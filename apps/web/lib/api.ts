const API_BASE=process.env.NEXT_PUBLIC_API_BASE_URL||'http://localhost:8000';
export async function scanText(content:string, enhanced=false, url?:string){const res=await fetch(`${API_BASE}/api/v1/scan/text`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({content,enhanced,url})});if(!res.ok)throw new Error('Scan failed');return res.json();}
export {API_BASE};
