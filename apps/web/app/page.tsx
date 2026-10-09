'use client';

import dynamic from 'next/dynamic';
import Scanner from '@/components/Scanner';
import { ArrowUpRight, Eye, Lock, Mic, ScanSearch } from 'lucide-react';

const HeroOrb = dynamic(() => import('@/components/HeroOrb'), { ssr: false });

const threatCards = [
  ['Fake bank alerts', 'Account blocked', 'Credential phishing'],
  ['Prize bait', 'You won money', 'Payment scam'],
  ['Fake support', 'Device infected', 'Remote access'],
  ['Family emergency', 'Send money now', 'Impersonation']
];

export default function Home() {
  return (
    <main className="overflow-hidden paper-noise">
      <section className="relative border-b border-black/10">
        <div className="pointer-events-none absolute inset-0 fade-grid opacity-60" />
        <nav className="relative mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
          <div className="serif text-2xl font-semibold tracking-tight">SafeScroll<span className="text-[#b83a32]">.</span></div>
          <div className="hidden items-center gap-7 text-sm text-[#655b51] md:flex"><a href="#how">How it works</a><a href="#privacy">Privacy</a><a href="#scanner">Scanner</a><a href="#security">Security</a></div>
          <a href="#scanner" className="rounded-full bg-[#211e1a] px-5 py-2.5 text-sm font-semibold !text-[#f8f4ec] shadow-sm hover:bg-black transition-colors">Try SafeScroll</a>
        </nav>

        <div className="relative mx-auto grid min-h-[760px] max-w-7xl items-center gap-10 px-6 pb-16 pt-6 lg:grid-cols-[1.03fr_.97fr] lg:px-10 lg:pb-24">
          <div className="max-w-3xl">
            <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-black/10 bg-white/50 px-4 py-2 text-xs uppercase tracking-[.18em] text-[#6b6054]"><span className="h-2 w-2 rounded-full bg-[#5d8065]" /> Privacy-first digital safety</div>
            <h1 className="serif max-w-4xl text-6xl leading-[.92] tracking-[-.045em] sm:text-7xl lg:text-[7rem]">Before you click,<br /><em className="font-normal text-[#6d6257]">know what you’re looking at.</em></h1>
            <p className="mt-8 max-w-xl text-lg leading-8 text-[#6c6258] sm:text-xl">SafeScroll explains suspicious messages, websites, links and screenshots in plain language—so people can make safer digital decisions without becoming cybersecurity experts.</p>
            <div className="mt-9 flex flex-wrap gap-3"><a href="#scanner" className="inline-flex items-center gap-2 rounded-full bg-[#211e1a] px-6 py-3.5 text-sm font-semibold !text-[#f8f4ec] shadow-lg shadow-black/10 hover:bg-black transition-colors">Try Live Scanner <ArrowUpRight size={17} /></a><a href="#how" className="rounded-full border border-black/10 bg-white/55 px-6 py-3.5 text-sm font-semibold hover:bg-white transition-colors">See how it works</a></div>
            <div className="mt-10 flex flex-wrap gap-5 text-xs uppercase tracking-[.16em] text-[#786d61]"><span>Local-first</span><span>•</span><span>Senior-friendly</span><span>•</span><span>Explainable</span></div>
          </div>
          <div className="relative"><HeroOrb /><div className="absolute left-0 top-16 rounded-2xl border border-black/10 bg-[#fcfaf5]/85 p-4 shadow-2xl shadow-black/10 backdrop-blur-md"><div className="text-[10px] uppercase tracking-[.18em] text-[#7c7164]">Live signal</div><div className="mt-1 serif text-xl">Scanning for pressure…</div></div><div className="absolute bottom-12 right-0 max-w-[250px] rounded-2xl bg-[#211e1a] p-4 text-[#f8f4ec] shadow-2xl"><div className="text-[10px] uppercase tracking-[.18em] text-white/45">SafeScroll result</div><div className="mt-1 serif text-2xl">🔴 High risk</div><p className="mt-2 text-sm leading-5 text-white/65">“Someone is asking for your private security code.”</p></div></div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-24 lg:px-10"><div className="grid gap-12 lg:grid-cols-[.8fr_1.2fr]"><div><div className="text-xs uppercase tracking-[.2em] text-[#7a6f63]">The problem</div><h2 className="serif mt-4 text-5xl leading-tight sm:text-6xl">Scams don’t look like scams anymore.</h2></div><div className="grid gap-4 sm:grid-cols-2">{threatCards.map(([title, phrase, category], i) => <div key={title} className="rounded-[26px] border border-black/10 bg-[#f1e8d8] p-6"><div className="text-xs uppercase tracking-[.16em] text-[#8a7f73]">0{i + 1}</div><div className="serif mt-12 text-2xl">{title}</div><div className="mt-3 text-sm text-[#766c60]">{phrase} · {category}</div></div>)}</div></div></section>

      <section id="how" className="border-y border-black/10 bg-[#eee4d3] px-6 py-24 lg:px-10"><div className="mx-auto max-w-7xl"><div className="max-w-2xl"><div className="text-xs uppercase tracking-[.2em] text-[#7a6f63]">How it works</div><h2 className="serif mt-4 text-5xl leading-tight">A second thought, before a risky action.</h2></div><div className="mt-16 grid gap-5 lg:grid-cols-3">{[
        { icon: ScanSearch, num: '01', title: 'Scan', copy: 'A message, website, screenshot or link.' },
        { icon: Eye, num: '02', title: 'Understand', copy: 'Signals are combined into a clear risk assessment.' },
        { icon: Mic, num: '03', title: 'Act safely', copy: 'You get simple explanations and the next safest step.' }
      ].map((step) => { const I = step.icon; return <div key={step.num} className="rounded-[28px] bg-[#fcfaf5] p-7 shadow-[0_18px_60px_rgba(70,55,35,.07)]"><div className="flex items-center justify-between"><div className="text-xs uppercase tracking-[.2em] text-[#7a6f63]">{step.num}</div><I size={21}/></div><h3 className="serif mt-14 text-3xl">{step.title}</h3><p className="mt-3 leading-7 text-[#6f655a]">{step.copy}</p></div>; })}</div></div></section>

      <section id="scanner" className="mx-auto max-w-7xl px-6 py-24 lg:px-10"><div className="mb-10 flex flex-wrap items-end justify-between gap-6"><div><div className="text-xs uppercase tracking-[.2em] text-[#7a6f63]">Live Security Scanner</div><h2 className="serif mt-4 text-5xl leading-tight">See the explanation, not just the score.</h2></div><p className="max-w-md text-[#6f655a]">The core product experience is designed around evidence and action—not technical threat jargon.</p></div><Scanner /></section>

      <section id="privacy" className="border-y border-black/10 bg-[#211e1a] px-6 py-24 text-[#f8f4ec] lg:px-10"><div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[1fr_.9fr] lg:items-center"><div><div className="text-xs uppercase tracking-[.2em] text-white/45">Privacy by architecture</div><h2 className="serif mt-4 text-5xl leading-tight sm:text-6xl">Your private messages should stay private.</h2><p className="mt-6 max-w-2xl text-lg leading-8 text-white/65">SafeScroll is built local-first. OCR, rules, URL checks and voice can run on-device. Enhanced AI is an explicit opt-in path, not a hidden requirement.</p></div><div className="grid gap-3">{['Local-first scanning','No account required for ZERO mode','No raw message logging by default','Optional cloud intelligence with consent'].map((x) => <div key={x} className="rounded-2xl border border-white/10 bg-white/5 p-5 text-sm">✓ {x}</div>)}</div></div></section>

      <section id="security" className="mx-auto max-w-7xl px-6 py-24 lg:px-10"><div className="rounded-[36px] border border-black/10 bg-[#f1e8d8] p-8 sm:p-12"><div className="max-w-3xl"><div className="text-xs uppercase tracking-[.2em] text-[#7a6f63]">The principle</div><h2 className="serif mt-4 text-5xl leading-tight">Don’t make people become cybersecurity experts.</h2><p className="mt-6 text-xl leading-8 text-[#6d6257]">Make technology explain danger to them.</p></div><div className="mt-12 grid gap-4 sm:grid-cols-3"><div className="rounded-2xl bg-[#fcfaf5] p-5"><Lock size={20}/><div className="serif mt-8 text-2xl">Private</div><p className="mt-2 text-sm leading-6 text-[#756b60]">Local-first analysis and explicit cloud consent.</p></div><div className="rounded-2xl bg-[#fcfaf5] p-5"><Eye size={20}/><div className="serif mt-8 text-2xl">Understandable</div><p className="mt-2 text-sm leading-6 text-[#756b60]">Simple evidence instead of cybersecurity jargon.</p></div><div className="rounded-2xl bg-[#fcfaf5] p-5"><ScanSearch size={20}/><div className="serif mt-8 text-2xl">Actionable</div><p className="mt-2 text-sm leading-6 text-[#756b60]">Every warning ends with a practical next step.</p></div></div></div></section>

      <footer className="border-t border-black/10 px-6 py-10 lg:px-10"><div className="mx-auto flex max-w-7xl flex-col justify-between gap-6 sm:flex-row sm:items-center"><div><div className="serif text-xl">SafeScroll<span className="text-[#b83a32]">.</span></div><div className="mt-1 text-xs text-[#7b7064]">Digital safety, made understandable.</div></div><div className="flex flex-wrap gap-5 text-sm text-[#6e6459]"><a href="#privacy">Privacy</a><a href="#security">Security</a><a href="#scanner">Scanner</a></div></div></footer>
    </main>
  );
}
