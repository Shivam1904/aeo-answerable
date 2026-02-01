import { LayoutDashboard, LogOut } from 'lucide-react'
import { ThemeToggle } from './ThemeToggle'

interface NavbarProps {
    product?: {
        name: string
        domain?: string
    }
    user?: {
        username: string
    }
    // Actions extracted to Overview page
    onRefresh?: () => void
    isRefreshing?: boolean
}

export function Navbar({ product, user }: NavbarProps) {
    const handleLogout = () => {
        localStorage.removeItem('aeo_user')
        window.location.href = '/'
    }

    return (
        <nav className="fixed top-0 w-full z-50 border-b border-border bg-background/80 backdrop-blur-md">
            <div className="max-w-screen-2xl mx-auto px-6 h-16 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <a href="/products" className="font-semibold tracking-tight text-text-primary hidden sm:block hover:text-text-secondary transition-colors">
                        Answerable
                    </a>
                </div>

                <div className="flex items-center gap-6">
                    <ThemeToggle />

                    {/* User Info (always show if available, simple version) */}
                    {user && (
                        <span className="text-sm text-text-secondary hidden sm:block">
                            Logged in as <span className="text-text-primary font-medium">{user.username}</span>
                        </span>
                    )}

                    {/* Projects Link (if we are deep in product view) */}
                    {product && (
                        <a href="/products" className="flex items-center gap-2 text-sm text-text-secondary hover:text-text-primary transition-colors">
                            <LayoutDashboard className="w-4 h-4" />
                            <span className="hidden sm:inline">Projects</span>
                        </a>
                    )}

                    {/* Logout */}
                    <button onClick={handleLogout} className="flex items-center gap-2 text-sm text-text-secondary hover:text-red-400 transition-colors">
                        <LogOut className="w-4 h-4" />
                        <span className="hidden sm:inline">Logout</span>
                    </button>
                </div>
            </div>
        </nav>
    )
}
