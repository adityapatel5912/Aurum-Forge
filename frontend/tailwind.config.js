/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        cream: "#FFFBF0",
        navy: {
          DEFAULT: "#0A1931",
          soft: "#16294a",
          mute: "#3d4f6d",
        },
        gold: {
          DEFAULT: "#C6A96B",
          soft: "#E4D3AC",
          deep: "#A98B4F",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(10,25,49,0.06), 0 8px 24px -12px rgba(10,25,49,0.18)",
        forge: "0 6px 20px -6px rgba(198,169,107,0.55)",
      },
    },
  },
  plugins: [],
};
