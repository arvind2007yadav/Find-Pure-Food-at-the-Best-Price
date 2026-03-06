/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.amazon.in" },
      { protocol: "https", hostname: "**.amazon.com" },
      { protocol: "https", hostname: "**.flipkart.com" },
      { protocol: "https", hostname: "**.flixcart.com" },
      { protocol: "https", hostname: "**.shopify.com" },
      { protocol: "https", hostname: "**.anveshan.farm" },
      { protocol: "https", hostname: "**.rosierfoods.com" },
      { protocol: "https", hostname: "**.twobrothersindiashop.com" },
      { protocol: "https", hostname: "**.batiora.com" },
    ],
  },
};

module.exports = nextConfig;
