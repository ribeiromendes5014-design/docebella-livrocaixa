/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",        // templates globais
    "./**/templates/**/*.html",     // templates dos apps Django
    "./static/**/*.js",             // arquivos JS
    "./static/**/*.css",            // CSS com @apply
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#2563eb",
          light: "#3b82f6",
          dark: "#1e40af",
        },
        secondary: "#facc15",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
      },
      boxShadow: {
        soft: "0 4px 14px rgba(0,0,0,0.08)",
      },
    },
  },
  darkMode: "class",
  plugins: [],
};
