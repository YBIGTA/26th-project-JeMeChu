import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export", // ✅ Enables static export
  images: {
    unoptimized: true, // ✅ Ensures images work in static exports
  },
};

export default nextConfig;
