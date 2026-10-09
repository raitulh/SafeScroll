import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SafeScroll — Before you click, know what you are looking at.',
  description: 'A privacy-first digital safety assistant for suspicious messages, websites, links and screenshots.',
  metadataBase: new URL('http://localhost:3000'),
  openGraph: {
    title: 'SafeScroll',
    description: 'Digital safety, made understandable.',
    type: 'website'
  }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
