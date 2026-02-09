import { useState } from 'react'
import { Copy, Check, Terminal } from 'lucide-react'

interface SchemaFixerProps {
    domain: string
    title: string
}

export function SchemaFixer({ domain, title }: SchemaFixerProps) {
    const [copied, setCopied] = useState(false)

    const schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": title || domain,
        "url": `https://${domain}`,
        "logo": `https://${domain}/logo.png`,
        "sameAs": [
            `https://twitter.com/${domain.split('.')[0]}`,
            `https://linkedin.com/company/${domain.split('.')[0]}`
        ],
        "potentialAction": {
            "@type": "SearchAction",
            "target": `https://${domain}/search?q={search_term_string}`,
            "query-input": "required name=search_term_string"
        }
    }

    const schemaString = JSON.stringify(schema, null, 2)

    const handleCopy = () => {
        navigator.clipboard.writeText(`<script type="application/ld+json">\n${schemaString}\n</script>`)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <div className="bg-background border border-border rounded-xl overflow-hidden">
            <div className="px-4 py-2 bg-surface-secondary border-b border-border flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Terminal className="w-3.5 h-3.5 text-text-secondary" />
                    <span className="text-[10px] font-bold uppercase tracking-widest text-text-secondary">Generated JSON-LD Schema</span>
                </div>
                <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-2 py-1 hover:bg-surface rounded transition-colors text-indigo-400"
                >
                    {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span className="text-[10px] font-bold uppercase">{copied ? 'Copied' : 'Copy'}</span>
                </button>
            </div>
            <div className="p-4 bg-zinc-950 font-mono text-[11px] leading-relaxed text-emerald-500/90 overflow-x-auto max-h-[300px] scrollbar-thin">
                <pre>
                    {`<script type="application/ld+json">\n${schemaString}\n</script>`}
                </pre>
            </div>
        </div>
    )
}
