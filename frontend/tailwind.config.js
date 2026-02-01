/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                background: 'var(--background)',
                surface: 'var(--surface)',
                'surface-highlight': 'var(--surface-highlight)',
                border: 'var(--border)',
                primary: 'var(--primary)',
            },
            textColor: {
                primary: 'var(--text-primary)',
                secondary: 'var(--text-secondary)',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
            backgroundImage: {
                'dot-pattern': 'radial-gradient(#e5e7eb 1px, transparent 1px)',
            },
            backgroundSize: {
                'dot': '24px 24px',
            },
            keyframes: {
                shimmer: {
                    '100%': { transform: 'translateX(100%)' },
                }
            },
            animation: {
                shimmer: 'shimmer 2s infinite',
            }
        },
    },
    plugins: [],
}
