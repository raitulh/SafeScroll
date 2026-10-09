'use client';

import { useState } from 'react';
import { analyzeText, type ScanResult } from '@safescroll/detection-core';
import { scanText } from '../lib/api';
import { Volume2, ShieldAlert, CircleCheck, TriangleAlert, Trash2, ArrowRight } from 'lucide-react';

function speak(text: string) {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
}

export default function Scanner() {
  const [content, setContent] = useState('');
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const scan = async () => {
    const trimmed = content.trim();
    if (!trimmed) {
      setError('Please enter some text or a link to scan.');
      return;
    }
    setError(null);
    setScanning(true);
    setResult(null);

    try {
      // Try live backend API first
      const apiResult = await scanText(trimmed);
      setResult(apiResult);
    } catch {
      // Seamlessly fall back to local detection core
      await new Promise((r) => setTimeout(r, 400));
      setResult(analyzeText(trimmed));
    } finally {
      setScanning(false);
    }
  };

  const handleClear = () => {
    setContent('');
    setResult(null);
    setError(null);
  };

  const Icon = result?.severity === 'SCAM' ? ShieldAlert : result?.severity === 'SUSPICIOUS' ? TriangleAlert : CircleCheck;

  return (
    <div className="grid gap-5 lg:grid-cols-[1fr_0.9fr]">
      <div className="flex flex-col justify-between rounded-[28px] border border-black/10 bg-[#fcfaf5] p-6 shadow-[0_20px_70px_rgba(70,55,35,.08)]">
        <div>
          <div className="mb-4 flex items-center justify-between text-xs uppercase tracking-[.18em] text-[#756b60]">
            <span>Your Content</span>
            <div className="flex items-center gap-3">
              {content && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="inline-flex items-center gap-1 text-xs text-[#b83a32] hover:underline"
                >
                  <Trash2 size={13} /> Clear
                </button>
              )}
              <span>Live Scanner</span>
            </div>
          </div>

          <div className="relative">
            <textarea
              value={content}
              onChange={(e) => {
                setContent(e.target.value);
                if (error) setError(null);
              }}
              placeholder="Paste or type any real message, SMS, email, suspicious website link, or security alert here..."
              rows={6}
              className="w-full resize-none rounded-2xl border border-black/10 bg-[#f1e8d8] p-4 text-[17px] leading-7 text-[#211e1a] placeholder-[#8d8073] focus:border-[#211e1a] focus:bg-[#f8f4ec] focus:outline-none transition-all"
            />
          </div>

          {error && <p className="mt-2 text-xs text-[#b83a32]">{error}</p>}

          <div className="mt-3 flex items-center justify-between text-xs text-[#8a7f73]">
            <span>Supports English, Bangla & links</span>
            <span>{content.length} characters</span>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            onClick={scan}
            disabled={scanning || !content.trim()}
            className="flex-1 inline-flex items-center justify-center gap-2 rounded-full bg-[#211e1a] px-6 py-3.5 text-sm font-semibold !text-[#f8f4ec] shadow-md transition hover:bg-black disabled:cursor-not-allowed disabled:opacity-40"
          >
            {scanning ? 'Analyzing signals…' : 'Scan with SafeScroll'}
            {!scanning && <ArrowRight size={16} />}
          </button>
          {content && (
            <button
              onClick={handleClear}
              type="button"
              className="rounded-full border border-black/15 bg-white/70 px-5 py-3.5 text-sm font-medium text-[#5c5247] hover:bg-white transition"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="rounded-[28px] border border-black/10 bg-[#211e1a] p-6 text-[#f8f4ec] shadow-[0_20px_70px_rgba(50,40,30,.12)]">
        {!result && !scanning && (
          <div className="flex min-h-[320px] flex-col items-center justify-center gap-2 text-center text-[#cfc5b8]">
            <p className="serif text-2xl text-white/80">Ready to analyze</p>
            <p className="max-w-xs text-sm text-white/50">
              Type or paste your message or link on the left and click scan to see plain-language safety explanations.
            </p>
          </div>
        )}
        {scanning && (
          <div className="flex min-h-[320px] flex-col items-center justify-center gap-5 text-center">
            <div className="h-12 w-12 animate-spin rounded-full border-2 border-white/20 border-t-white" />
            <p className="serif text-3xl">Looking for pressure, requests, and risky signals…</p>
          </div>
        )}
        {result && (
          <div className="transition-all duration-300">
            <div className="flex items-center gap-3">
              <Icon size={28} />
              <div>
                <div className="text-xs uppercase tracking-[.2em] text-white/55">Assessment</div>
                <div className="serif text-4xl">{result.severity.replace('_', ' ')}</div>
              </div>
              <div className="ml-auto text-right">
                <div className="text-xs text-white/50">Risk Score</div>
                <div className="text-3xl font-semibold">{result.score}/100</div>
              </div>
            </div>
            <p className="mt-7 max-w-md text-base leading-7 text-white/75">{result.explanation}</p>
            {result.evidence && result.evidence.length > 0 && (
              <div className="mt-6 flex flex-wrap gap-2">
                {result.evidence.map((e) => (
                  <span
                    key={e.code}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs text-white/75"
                  >
                    {e.label}
                  </span>
                ))}
              </div>
            )}
            {result.actions && result.actions.length > 0 && (
              <div className="mt-7 rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="text-xs uppercase tracking-[.18em] text-white/45">What to do</div>
                <ul className="mt-3 space-y-2 text-sm text-white/75">
                  {result.actions.map((a) => (
                    <li key={a}>• {a}</li>
                  ))}
                </ul>
              </div>
            )}
            <button
              onClick={() =>
                speak(`${result.severity}. ${result.explanation} ${(result.actions || []).join(' ')}`)
              }
              className="mt-5 inline-flex items-center gap-2 rounded-full bg-[#f8f4ec] px-4 py-2.5 text-sm font-semibold !text-[#211e1a] hover:bg-white transition"
            >
              <Volume2 size={16} /> Read warning aloud
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
