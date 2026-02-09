import { useState, useEffect } from 'react'
import { Terminal, CheckCircle2, Loader2, Globe, BrainCircuit } from 'lucide-react'

const STEPS = [
    { id: 1, text: 'Connecting to Neural Network...', icon: Terminal, delay: 0 },
    { id: 2, text: 'Simulating AI Perception...', icon: BrainCircuit, delay: 1500 },
    { id: 3, text: 'Evaluating Content Authority...', icon: Globe, delay: 3000 },
    { id: 4, text: 'Generating Answerability Score...', icon: CheckCircle2, delay: 5000 },
]

export function SmartLoader() {
    const [currentStep, setCurrentStep] = useState(0)

    useEffect(() => {
        // Simulate progress through steps
        const timeouts = STEPS.map((step, index) => {
            return setTimeout(() => {
                setCurrentStep(index + 1)
            }, step.delay)
        })

        return () => timeouts.forEach(clearTimeout)
    }, [])

    return (
        <div className="flex flex-col items-center justify-center min-h-[50vh] max-w-lg mx-auto p-8 w-full">
            <div className="w-16 h-16 relative mb-8">
                <div className="absolute inset-0 border-4 border-indigo-500/30 rounded-full animate-pulse"></div>
                <div className="absolute inset-0 border-4 border-t-indigo-500 rounded-full animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                    <Terminal className="w-6 h-6 text-indigo-400" />
                </div>
            </div>

            <h2 className="text-2xl font-bold text-text-primary mb-8 text-center">Auditing your Product</h2>

            <div className="w-full space-y-4 font-mono text-sm max-w-md">
                {STEPS.map((step, index) => {
                    const isActive = index + 1 === currentStep
                    const isComplete = index + 1 < currentStep
                    const isPending = index + 1 > currentStep

                    return (
                        <div
                            key={step.id}
                            className={`flex items-center gap-4 transition-all duration-500 ${isPending ? 'opacity-30 translate-y-2' : 'opacity-100 translate-y-0'
                                }`}
                        >
                            <div className={`
                                w-6 h-6 rounded flex items-center justify-center transition-colors
                                ${isComplete ? 'bg-green-500/20 text-green-400' :
                                    isActive ? 'bg-indigo-500/20 text-indigo-400' : 'bg-surface-highlight text-text-secondary'}
                            `}>
                                {isComplete ? <CheckCircle2 className="w-4 h-4" /> :
                                    isActive ? <Loader2 className="w-4 h-4 animate-spin" /> :
                                        <step.icon className="w-3 h-3" />}
                            </div>
                            <span className={isComplete ? 'text-text-secondary/60' : isActive ? 'text-text-primary font-medium' : 'text-text-secondary'}>
                                {step.text}
                            </span>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
