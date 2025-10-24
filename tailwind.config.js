/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './*.html',                    // base.html, base_admin.html, etc. na raiz
    './**/*.html',                 // qualquer HTML dentro de subpastas
    './**/templates/**/*.html',    // compatível com apps Django que tenham templates próprios
    './**/*.py',                   // detectar classes inline em views Python
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
