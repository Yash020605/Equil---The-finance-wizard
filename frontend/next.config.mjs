/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',   // Required for the Docker multi-stage build
};

export default nextConfig;
