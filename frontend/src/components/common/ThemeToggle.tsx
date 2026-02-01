import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext'

export function ThemeToggle() {
    const { theme, toggleTheme } = useTheme()

    return (
        <button
            onClick={toggleTheme}
            className="p-2 rounded-md hover:bg-surface-highlight text-text-secondary hover:text-text-primary transition-colors"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
            {theme === 'dark' ? (
                <Sun className="w-4 h-4" />
            ) : (
                <Moon className="w-4 h-4" />
            )}
            <span className="sr-only">Toggle theme</span>
        </button>
    )
}
