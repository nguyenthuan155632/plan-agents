/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './node_modules/streamdown/dist/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        'agent-a': '#3b82f6',
        'agent-b': '#a855f7',
        'human': '#10b981',
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}

