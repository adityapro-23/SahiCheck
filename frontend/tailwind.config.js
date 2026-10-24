/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', "system-ui", "sans-serif"],
      },
      colors: {
        // Core palette tokens from the design reference
        surface:           "#f8f9ff",
        "on-surface":      "#0d1c2f",
        "primary-container": "#0d1c32",
        "primary-hover":   "#132847",
        // Status colours
        passed:  { DEFAULT: "#166534", bg: "#dcfce7", text: "#14532d" },
        failed:  { DEFAULT: "#991b1b", bg: "#fee2e2", text: "#7f1d1d" },
        neutral: { DEFAULT: "#64748b", bg: "#f1f5f9", text: "#475569" },
        info:    { DEFAULT: "#1d4ed8", bg: "#dbeafe", text: "#1e3a8a" },
        // Score band colours
        green:   { DEFAULT: "#15803d", light: "#dcfce7" },
        amber:   { DEFAULT: "#b45309", light: "#fef3c7" },
        red:     { DEFAULT: "#b91c1c", light: "#fee2e2" },
      },
      boxShadow: {
        card: "0 4px 24px rgba(13,28,47,0.07)",
        modal: "0 20px 48px -12px rgba(13,28,47,0.18)",
      },
    },
  },
  plugins: [],
};
