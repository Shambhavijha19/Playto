/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Subtle, muted color palette
        'sand': {
          50: '#faf9f7',
          100: '#f5f3ef',
          200: '#e8e4dc',
          300: '#d4cfc3',
          400: '#b8b0a0',
          500: '#9a9080',
          600: '#7a7164',
          700: '#5c5549',
          800: '#3d3a32',
          900: '#1f1e1a',
        }
      }
    },
  },
  plugins: [],
}
