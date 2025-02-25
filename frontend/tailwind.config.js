/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        gmarket: ["GmarketSans", "sans-serif"],
        ibm: ["IBM Plex Sans KR", "sans-serif"],
      },
    },
  },
  plugins: [],
};
