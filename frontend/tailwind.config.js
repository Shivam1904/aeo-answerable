/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
            backgroundImage: {
                'dot-pattern': 'radial-gradient(#e5e7eb 1px, transparent 1px)',
            },
            backgroundSize: {
                'dot': '24px 24px',
            }
        },
    },
    plugins: [],
}
