import Link from 'next/link';
export function StaticPage({eyebrow,title,children,paragraphs}:{eyebrow:string;title:string;children?:React.ReactNode;paragraphs?:string[]}){
 return <main className="min-h-screen bg-[#f8f4ec] px-6 py-10 text-[#211e1a] lg:px-10"><div className="mx-auto max-w-5xl"><Link href="/" className="serif text-2xl">SafeScroll<span className="text-[#b83a32]">.</span></Link><div className="mt-24 max-w-3xl"><div className="text-xs uppercase tracking-[.2em] text-[#7a6f63]">{eyebrow}</div><h1 className="serif mt-4 text-6xl leading-[.95] tracking-[-.035em]">{title}</h1><div className="mt-10 space-y-7 text-lg leading-8 text-[#6d6257]">{paragraphs ? paragraphs.map((p, i) => <p key={i}>{p}</p>) : children}</div></div></div></main>
}
