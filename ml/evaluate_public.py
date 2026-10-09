#!/usr/bin/env python3
import json, math, re
from pathlib import Path

def sigmoid(z): return 1/(1+math.exp(-max(-30,min(30,z))))
def h32(s):
    h=2166136261
    for b in s.encode('utf-8'):
        h^=b; h=(h*16777619)&0xffffffff
    return h
def vec(t,n):
    s=' '.join(t.lower().split()); x=[0.0]*n
    for k in range(2,6):
        for i in range(max(0,len(s)-k+1)): x[h32(s[i:i+k])%n]+=1
    norm=math.sqrt(sum(v*v for v in x)) or 1; return [v/norm for v in x]

def main():
    model=json.loads(Path('apps/extension/public/models/scam-classifier/model.json').read_text())
    data=Path('ml/data/public/SMSSpamCollection').read_text(encoding='utf-8').splitlines()
    rows=[(line.split('	',1)[1],1 if line.split('	',1)[0]=='spam' else 0) for line in data if '	' in line]
    yhat=[]
    for text,label in rows:
        x=vec(text,model['n_features']); z=sum(a*b for a,b in zip(model['weights'],x))+model['bias']; p=sigmoid(z/max(model['temperature'],1e-6)); yhat.append((p,label))
    for threshold in (0.3,0.5,0.7):
        tp=sum(p>=threshold and y==1 for p,y in yhat); fp=sum(p>=threshold and y==0 for p,y in yhat); fn=sum(p<threshold and y==1 for p,y in yhat); tn=sum(p<threshold and y==0 for p,y in yhat)
        precision=tp/max(1,tp+fp); recall=tp/max(1,tp+fn); f1=2*precision*recall/max(1,precision+recall)
        print(json.dumps({'threshold':threshold,'precision':precision,'recall':recall,'f1':f1,'accuracy':(tp+tn)/max(1,len(yhat))}))
if __name__=='__main__':main()
