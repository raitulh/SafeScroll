#!/usr/bin/env python3
"""Fetch the UCI SMS Spam Collection metadata/data for reproducible benchmark training.
The dataset is CC BY 4.0; keep attribution in docs and do not silently redistribute it in release artifacts.
"""
from pathlib import Path
import urllib.request, zipfile, io
URL='https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip'
out=Path('ml/data/public'); out.mkdir(parents=True,exist_ok=True)
raw=urllib.request.urlopen(URL,timeout=30).read(); z=zipfile.ZipFile(io.BytesIO(raw)); z.extractall(out)
print('Fetched UCI SMS Spam Collection to',out)
