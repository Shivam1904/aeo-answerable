import { Info } from 'lucide-react'

export function MetricTooltip({ description }: { description: string }) {
    return (
        <div className="group relative flex items-center">
            <Info className="w-3 h-3 text-zinc-600 hover:text-zinc-400 transition-colors cursor-help" />

            {/* Tooltip Content */}
            <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-48 p-2 
                          bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl 
                          opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                <p className="text-[10px] text-zinc-400 font-medium leading-relaxed text-center">
                    {description}
                </p>
                {/* Arrow */}
                <div className="absolute left-1/2 -translate-x-1/2 top-100 w-2 h-2 
                              bg-zinc-900 border-r border-b border-zinc-800 rotate-45 transform translate-y-[-50%]" />
            </div>
        </div>
    )
}
