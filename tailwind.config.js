cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
const path = require("path");

module.exports = {
  content: [
    path.join(__dirname, "templates/**/*.html"),
    path.join(__dirname, "**/templates/**/*.html"),
    path.join(__dirname, "static/**/*.js"),
    path.join(__dirname, "static/**/*.css"),
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
EOF
