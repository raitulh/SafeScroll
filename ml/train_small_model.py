#!/usr/bin/env python3
"""Train a tiny hashed-character logistic model that can run inside the extension.
This is a lightweight bootstrap model. For production promotion, train with licensed public corpora
via ml/fetch_public_data.py and require the evaluation gate to pass.
"""
import argparse, json, math, re, random
from pathlib import Path
from typing import Iterable

N=2048

def tokens(text:str):
    s=' '.join(text.lower().split())
    grams=[]
    for n in range(2,6):
        for i in range(max(0,len(s)-n+1)):
            grams.append(s[i:i+n])
    return grams

def h32(s:str):
    h=2166136261
    for b in s.encode('utf-8'):
        h ^= b; h=(h*16777619)&0xffffffff
    return h

def vec(text):
    x=[0.0]*N; grams=tokens(text)
    if not grams:return x
    for g in grams:x[h32(g)%N]+=1.0
    norm=math.sqrt(sum(v*v for v in x)) or 1.0
    return [v/norm for v in x]

def sigmoid(z):return 1/(1+math.exp(-max(-30,min(30,z))))

def read(path):return [json.loads(x) for x in Path(path).read_text(encoding='utf-8').splitlines() if x.strip()]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data',default='ml/data/seed.jsonl'); ap.add_argument('--out',default='apps/extension/public/models/scam-classifier/model.json'); args=ap.parse_args()
    rows=read(args.data); random.Random(7).shuffle(rows); split=max(4,int(len(rows)*0.8)); train,valid=rows[:split],rows[split:]
    w=[0.0]*N; b=0.0; lr=0.35
    for epoch in range(40):
        random.Random(epoch).shuffle(train)
        for r in train:
            x=vec(r['text']); p=sigmoid(sum(a*c for a,c in zip(w,x))+b); err=p-r['label']
            for i,c in enumerate(x): w[i]-=lr*err*c*0.002
            b-=lr*err*0.02
        lr*=0.96
    def probs(rows): return [(sigmoid(sum(a*c for a,c in zip(w,vec(r['text'])))+b),r['label']) for r in rows]
    # simple Platt-like temperature search on validation set
    pv=probs(valid); best=(9e9,1.0)
    for t in [0.6+i*0.02 for i in range(51)]:
        loss=0.0
        for p,y in pv:
            logit=math.log(max(1e-6,p)/max(1e-6,1-p))/t; q=sigmoid(logit); loss += -(y*math.log(max(q,1e-6))+(1-y)*math.log(max(1-q,1e-6)))
        if loss<best[0]:best=(loss,t)
    out={'version':'small-linear-1.0','n_features':N,'hash':'fnv1a32-char-ngram-2-5','weights':w,'bias':b,'temperature':best[1],'trained_examples':len(train)}
    Path(args.out).parent.mkdir(parents=True,exist_ok=True); Path(args.out).write_text(json.dumps(out,separators=(',',':')),encoding='utf-8')
    meta={'model':out['version'],'trained_examples':len(train),'validation_examples':len(valid),'temperature':best[1],'note':'Bootstrap model from repository seed. Retrain on licensed public corpus before production promotion.'}
    Path('ml/evaluation/latest.json').parent.mkdir(parents=True,exist_ok=True); Path('ml/evaluation/latest.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
