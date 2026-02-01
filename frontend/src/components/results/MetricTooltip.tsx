import { Info } from 'lucide-react'

export function MetricTooltip({ description }: { description: string }) {
    return (
        <div className="group relative flex items-center">
            <Info className="w-3 h-3 text-text-secondary hover:text-text-primary transition-colors cursor-help" />

            {/* Tooltip Content */}
            <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-48 p-2 
                          bg-surface border border-border rounded-lg shadow-xl 
                          opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                <p className="text-[10px] text-text-secondary font-medium leading-relaxed text-center">
                    {description}
                </p>
                {/* Arrow */}
                <div className="absolute left-1/2 -translate-x-1/2 top-100 w-2 h-2 
                              bg-surface border-r border-b border-border rotate-45 transform translate-y-[-50%]" />
            </div>
        </div>
    )
}
