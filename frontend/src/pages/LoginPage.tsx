import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Bot } from 'lucide-react'
import { api } from '../api'
import { ThemeToggle } from '../components/common/ThemeToggle'

export default function LoginPage() {
    const [username, setUsername] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')
    const navigate = useNavigate()

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!username.trim()) return

        setIsLoading(true)
        setError('')

        try {
            const data = await api.auth.login(username.trim())
            localStorage.setItem('aeo_user', JSON.stringify(data))
            navigate('/products')
        } catch (err: any) {
            setError('Login failed. Please try again.')
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-background flex flex-col relative overflow-hidden font-sans selection:bg-indigo-500/30 selection:text-indigo-200 transition-colors duration-300">
            {/* Background Effects */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/20 rounded-full blur-[128px] pointer-events-none opacity-50 dark:opacity-100" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[128px] pointer-events-none opacity-50 dark:opacity-100" />

            <nav className="relative z-50 p-6 flex justify-between items-center max-w-7xl mx-auto w-full">
                <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-semibold tracking-tight text-text-primary">Answerable</span>
                </div>
                <div>
                    <ThemeToggle />
                </div>
            </nav>

            <main className="flex-1 flex flex-col items-center justify-center text-center px-6 relative z-10 w-full max-w-5xl mx-auto space-y-12 pb-20">

                <div className="space-y-6">
                    <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-text-primary leading-tight">
                        Make your content <br />
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500">
                            Answer-Ready.
                        </span>
                    </h1>

                    <p className="text-xl text-text-secondary max-w-2xl mx-auto font-light leading-relaxed">
                        The SEO era is fading. AEO is here. <br />
                        Audit your site's ability to be understood, retrieved, and cited by AI.
                    </p>
                </div>

                {/* Login Form */}
                <div className="w-full max-w-sm mx-auto">
                    <form onSubmit={handleLogin} className="relative group">
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl opacity-30 group-hover:opacity-60 blur transition duration-500"></div>
                        <div className="relative bg-surface rounded-xl flex items-center p-1.5 border border-border">
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="Enter username to start"
                                className="flex-1 bg-transparent text-text-primary placeholder-text-secondary outline-none text-base h-12 px-4"
                                autoFocus
                            />
                            <button
                                type="submit"
                                disabled={isLoading || !username.trim()}
                                className="px-6 h-12 bg-text-primary text-background font-medium rounded-lg hover:opacity-90 transition-opacity flex items-center gap-2 disabled:opacity-50"
                            >
                                {isLoading ? (
                                    <div className="w-4 h-4 border-2 border-background/30 border-t-background rounded-full animate-spin" />
                                ) : (
                                    <ArrowRight className="w-4 h-4" />
                                )}
                            </button>
                        </div>
                    </form>
                    {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
                </div>
            </main>
        </div>
    )
}
