/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/debate/:path*',
        destination: 'http://127.0.0.1:8000/api/debate/:path*',
      },
    ]
  },
}

