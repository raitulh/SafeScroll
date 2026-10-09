import model from '../../public/models/scam-classifier/model.json';

type LocalModel={version:string;n_features:number;hash:string;weights:number[];bias:number;temperature:number};
const M=model as unknown as LocalModel;

function h32(s:string){let h=2166136261; for(const b of new TextEncoder().encode(s)){h^=b; h=Math.imul(h,16777619)>>>0;} return h>>>0;}
function sigmoid(z:number){z=Math.max(-30,Math.min(30,z)); return 1/(1+Math.exp(-z));}
function vectorize(text:string){const x=new Float32Array(M.n_features); const s=text.toLowerCase().replace(/\s+/g,' ').trim(); let count=0; for(let n=2;n<=5;n++){for(let i=0;i<=s.length-n;i++){const g=s.slice(i,i+n); x[h32(g)%M.n_features]+=1; count++;}} let norm=0; for(const v of x) norm+=v*v; norm=Math.sqrt(norm)||1; for(let i=0;i<x.length;i++) x[i]/=norm; return x;}
export function localModelRisk(text:string){const x=vectorize(text.slice(0,12000)); let z=M.bias; for(let i=0;i<x.length;i++) z += M.weights[i]*x[i]; const calibrated=sigmoid(z/Math.max(M.temperature,0.25)); return {version:M.version, probability:calibrated};}
