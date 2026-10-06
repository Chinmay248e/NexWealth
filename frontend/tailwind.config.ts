import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: "#060d13",
          surface: "#0a151f",
          elevated: "#0f1f2d",
        },
        card: {
          DEFAULT: "#0c1824",
          hover: "#102130",
          subtle: "#08121a",
        },
        cyan: {
          DEFAULT: "#00f2fe",
          glow: "rgba(0, 242, 254, 0.25)",
          subtle: "rgba(0, 242, 254, 0.12)",
          400: "#00d2eb",
          500: "#00f2fe",
          600: "#00b4cc",
        },
        mint: {
          DEFAULT: "#00f5a0",
          glow: "rgba(0, 245, 160, 0.25)",
          subtle: "rgba(0, 245, 160, 0.12)",
          400: "#34d399",
          500: "#00f5a0",
          600: "#10b981",
        },
        border: {
          subtle: "rgba(255, 255, 255, 0.06)",
          light: "rgba(255, 255, 255, 0.1)",
          accent: "rgba(0, 242, 254, 0.25)",
          mint: "rgba(0, 245, 160, 0.25)",
        },
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "-apple-system", "sans-serif"],
        display: ["Space Grotesk", "sans-serif"],
      },
      borderRadius: {
        xs: "6px",
        sm: "10px",
        md: "14px",
        lg: "18px",
        xl: "24px",
      },
      boxShadow: {
        "cyan-glow": "0 0 25px rgba(0, 242, 254, 0.2)",
        "mint-glow": "0 0 25px rgba(0, 245, 160, 0.2)",
        "card-subtle": "0 4px 20px -2px rgba(0, 0, 0, 0.5)",
      },
    },
  },
  plugins: [],
};

export default config;
