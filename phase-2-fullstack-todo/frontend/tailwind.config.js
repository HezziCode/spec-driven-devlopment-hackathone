/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: 'var(--font-ibm-plex-sans)',
        display: 'var(--font-dm-sans)',
      },
      colors: {
        'gradient-start': '#0d9488', // teal-600
        'gradient-end': '#0891b2',   // cyan-600
      },
      backgroundImage: {
        'gradient-teal-cyan': 'linear-gradient(135deg, #0d9488 0%, #0891b2 100%)',
      }
    },
  },
  plugins: [],
  darkMode: 'class', // Enable dark mode with class strategy
};