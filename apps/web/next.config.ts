import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  transpilePackages: ['@safescroll/detection-core'],
  reactStrictMode: true,
  poweredByHeader: false,
  experimental: {
    optimizePackageImports: ['lucide-react']
  }
};

export default nextConfig;
