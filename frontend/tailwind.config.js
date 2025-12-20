/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0F1A',
        surface: '#121826',
        border: '#1E2638',
        primary: {
          DEFAULT: '#5B61D1',
          hover: '#6A70E0', // slight brightness increase
        },
        text: {
          primary: '#E6E8F0',
          secondary: '#A1A6C3',
        },
        success: '#3DDC97',
        warning: '#FFB86C',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Space Grotesk', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
