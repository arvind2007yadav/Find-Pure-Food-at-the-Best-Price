import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-bricolage)", "Bricolage Grotesque", "sans-serif"],
      },
      colors: {
        green: { 500: "#22c55e", 600: "#16a34a" },
        yellow: { 500: "#eab308" },
        red: { 500: "#ef4444" },
        brand: {
          gold: "#d2b777",
          "gold-dark": "#978c3e",
          cream: "#f6edd9",
          offwhite: "#f9f6ee",
          charcoal: "#282828",
          border: "#e7e7e7",
        },
      },
    },
  },
  plugins: [],
};

export default config;
