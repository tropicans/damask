/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dominant: "#0b0f19",
        secondary: "#161f30",
        accent: "#6366f1",
      }
    },
  },
  plugins: [],
}
