import { AlertTriangle, CheckCircle2, ChevronRight, Lightbulb, ShieldCheck } from 'lucide-react'

interface ActionItem {
    type: string
    priority: 'high' | 'medium' | 'low'
    title: string
    description: string
    fix_action: string
}

interface ActionPlanProps {
    actions: ActionItem[]
    onFix?: (action: ActionItem) => void
}

export function ActionPlanWidget({ actions, onFix }: ActionPlanProps) {
    if (!actions || actions.length === 0) return null

    return (
        <div className="bg-surface border border-border rounded-xl overflow-hidden shadow-sm">
            <div className="p-6 border-b border-border bg-indigo-500/[0.02]">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-500/10 rounded-lg">
                        <Lightbulb className="w-5 h-5 text-indigo-400" />
                    </div>
                    <div>
                        <h3 className="text-base font-bold text-text-primary">AI Action Plan</h3>
                        <p className="text-xs text-text-secondary">Prioritized steps to improve your AI engine visibility.</p>
                    </div>
                </div>
            </div>

            <div className="divide-y divide-border">
                {actions.map((action, i) => (
                    <div key={i} className="p-6 hover:bg-surface-secondary transition-colors group">
                        <div className="flex items-start gap-4">
                            <div className="shrink-0 mt-1">
                                {action.priority === 'high' ? (
                                    <AlertTriangle className="w-5 h-5 text-rose-400" />
                                ) : action.type === 'schema' ? (
                                    <ShieldCheck className="w-5 h-5 text-emerald-400" />
                                ) : (
                                    <CheckCircle2 className="w-5 h-5 text-indigo-400" />
                                )}
                            </div>

                            <div className="flex-1 space-y-1">
                                <div className="flex items-center gap-2">
                                    <span className={`text-[10px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded ${action.priority === 'high' ? 'bg-rose-500/10 text-rose-400' : 'bg-indigo-500/10 text-indigo-400'
                                        }`}>
                                        {action.priority} priority
                                    </span>
                                    <h4 className="text-sm font-bold text-text-primary">{action.title}</h4>
                                </div>
                                <p className="text-xs text-text-secondary leading-relaxed max-w-2xl">
                                    {action.description}
                                </p>

                                <button
                                    onClick={() => onFix?.(action)}
                                    className="mt-4 flex items-center gap-2 text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors group-hover:translate-x-1 duration-300"
                                >
                                    {action.fix_action}
                                    <ChevronRight className="w-3.5 h-3.5" />
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
